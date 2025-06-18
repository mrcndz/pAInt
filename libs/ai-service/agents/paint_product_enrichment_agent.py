import asyncio
import json
import logging
from typing import Any, Dict

from config import config
from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
from shared.database import get_db
from shared.models import PaintProductModel as PaintProduct

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PaintProductEnrichmentAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=config.OPENAI_API_KEY,
            model=config.OPENAI_MODEL,
            temperature=config.TEMPERATURE,
            max_completion_tokens=config.MAX_TOKENS,
        )
        self._setup_agent()

    def _setup_agent(self):
        """Setup LangChain agent for content generation"""
        tools = [
            Tool(
                name="enrich_content",
                description="Generate both summary and usage tags for paint products. Returns JSON with 'summary' and 'tags' fields.",
                func=self._enrich_content_tool,
            ),
        ]

        prompt = hub.pull(
            "hwchase17/react"
        )  # https://smith.langchain.com/hub/hwchase17/react
        prompt = prompt.partial(
            system_message="""You are an AI assistant specialized in creating marketing content for Suvinil paint products. 
You help generate compelling product summaries and relevant usage tags that highlight the paint's benefits and ideal use cases.
Always write summaries in Portuguese (Brazilian) and focus on practical applications and aesthetic appeal.

When using the enrich_content tool, provide the paint data as a JSON string and return the JSON response directly."""
        )

        # Create agent with tools and prompt
        agent = create_react_agent(self.llm, tools, prompt)
        self.agent_executor = AgentExecutor(
            agent=agent, tools=tools, verbose=True, handle_parsing_errors=True
        )

    def _enrich_content_tool(self, paint_data_str: str) -> str:
        """Tool function for generating both product summary and usage tags"""
        try:
            paint_data = json.loads(paint_data_str)
            prompt = f"""
            Create both a compelling product summary and relevant usage tags for this paint:
            
            Product: {paint_data['name']}
            Color: {paint_data['color']}
            Surface Types: {', '.join(paint_data['surface_types'])}
            Environment: {paint_data['environment']}
            Finish: {paint_data['finish_type']}
            Features: {', '.join(paint_data.get('features', []))}
            Product Line: {paint_data['product_line']}
            Price: R$ {paint_data.get('price', 'N/A')}
            
            IMPORTANT: Return your response as a JSON object with exactly this structure:
            {{
                "summary": "2-3 sentence summary in Portuguese (Brazilian) highlighting key benefits, ideal use cases, and special features",
                "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"]
            }}
            
            For the summary: Write in Portuguese (Brazilian), focus on practical applications and aesthetic appeal.
            
            For the tags: Generate 3-5 relevant tags from these categories:
            - Room types: living-room, bedroom, kitchen, bathroom, office, kids-room
            - Style: modern, classic, minimalist, rustic, elegant, cozy, bold
            - Usage: high-traffic, low-maintenance, family-friendly, professional, luxury
            - Characteristics: durable, easy-clean, weather-resistant, eco-friendly, quick-dry
            
            Return only the JSON object, no additional text.
            """

            response = self.llm.invoke(prompt)
            content = response.content
            if isinstance(content, list):
                content = content[0] if content else ""
            return content.strip() if isinstance(content, str) else str(content).strip()

        except Exception as e:
            logger.error(f"Error generating content: {e}")
            try:
                paint_data = json.loads(paint_data_str)
                fallback_summary = f"Tinta {paint_data.get('color', '')} da linha {paint_data.get('product_line', '')} ideal para {paint_data.get('environment', '')}."
                fallback_tags = []
                if paint_data.get("environment") == "internal":
                    fallback_tags.append("interior")
                elif paint_data.get("environment") == "external":
                    fallback_tags.append("exterior")
                if "washable" in paint_data.get("features", []):
                    fallback_tags.append("easy-clean")
                if paint_data.get("product_line") == "Premium":
                    fallback_tags.append("luxury")

                return json.dumps({"summary": fallback_summary, "tags": fallback_tags})
            except:
                return json.dumps(
                    {"summary": "Tinta de qualidade da Suvinil.", "tags": ["interior"]}
                )

    def enrich_product(self, product: PaintProduct) -> Dict[str, Any]:
        """Enrich a single product with AI-generated content"""
        paint_data = {
            "name": product.name,
            "color": product.color,
            "surface_types": product.surface_types or [],
            "environment": product.environment,
            "finish_type": product.finish_type,
            "features": product.features or [],
            "product_line": product.product_line,
            "price": float(product.price) if product.price else None,
        }

        logger.info(f"Enriching product: {product.name}")

        try:
            # Single agent call to generate summary and tags
            paint_data_json = json.dumps(paint_data)
            result = self.agent_executor.invoke(
                {
                    "input": f"Use the enrich_content tool to generate both summary and tags for this paint product: {paint_data_json}"
                }
            )

            # Parse the agent's output to extract the JSON response
            agent_output = result["output"]

            if "```json" in agent_output:
                # Extract JSON from code block if present
                start = agent_output.find("```json") + 7
                end = agent_output.find("```", start)
                json_str = agent_output[start:end].strip()
            elif agent_output.startswith("{") and agent_output.endswith("}"):
                json_str = agent_output
            else:
                # Try to find JSON in the output
                import re

                json_match = re.search(r"\{.*\}", agent_output, re.DOTALL)
                json_str = json_match.group(0) if json_match else agent_output

            enriched_data = json.loads(json_str)

            return {
                "ai_summary": enriched_data.get(
                    "summary", "Tinta de qualidade da Suvinil."
                ),
                "usage_tags": enriched_data.get("tags", ["interior"]),
            }

        except Exception as e:
            logger.error(f"Error with agent enrichment: {e}")
            fallback_summary = f"Tinta {paint_data.get('color', '')} da linha {paint_data.get('product_line', '')} ideal para {paint_data.get('environment', '')}."
            fallback_tags = []
            if paint_data.get("environment") == "internal":
                fallback_tags.append("interior")
            elif paint_data.get("environment") == "external":
                fallback_tags.append("exterior")
            if "washable" in paint_data.get("features", []):
                fallback_tags.append("easy-clean")
            if paint_data.get("product_line") == "Premium":
                fallback_tags.append("luxury")

            return {
                "ai_summary": fallback_summary,
                "usage_tags": fallback_tags if fallback_tags else ["interior"],
            }

    def enrich_all_products(self, batch_size: int = 5):
        """Enrich all products in the database"""
        db = next(get_db())

        try:
            products = (
                db.query(PaintProduct).filter(PaintProduct.ai_summary.is_(None)).all()
            )

            logger.info(f"Found {len(products)} products to enrich")

            for i in range(0, len(products), batch_size):
                batch = products[i : i + batch_size]
                logger.info(
                    f"Processing batch {i//batch_size + 1}/{(len(products) + batch_size - 1)//batch_size}"
                )

                for product in batch:
                    try:
                        enriched_data = self.enrich_product(product)

                        # Update product in database
                        product.ai_summary = enriched_data["ai_summary"]
                        product.usage_tags = enriched_data["usage_tags"]

                        db.commit()
                        logger.info(f"Updated product {product.id}: {product.name}")
                        _ = asyncio.sleep(1)

                    except Exception as e:
                        logger.error(f"Error enriching product {product.id}: {e}")
                        db.rollback()
                        continue

        except Exception as e:
            logger.error(f"Error in batch enrichment: {e}")
        finally:
            db.close()
