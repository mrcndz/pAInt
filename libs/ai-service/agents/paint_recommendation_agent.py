import logging
from typing import List, Optional

from config import config
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import StructuredTool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from rag.vector_store_pg import get_vector_store

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PaintSearchArgs(BaseModel):
    query: str = Field(
        description="Search query for paint products (color, room type, features, etc.)"
    )
    limit: Optional[int] = Field(
        default=5, description="Maximum number of results to return"
    )


class PaintFilterArgs(BaseModel):
    environment: Optional[str] = Field(
        default=None,
        description="Environment type: 'internal' for indoor use or 'external' for outdoor use",
    )
    finish_type: Optional[str] = Field(
        default=None, description="Finish type: 'matte', 'satin', 'gloss', etc."
    )
    product_line: Optional[str] = Field(
        default=None, description="Product line: 'Premium', 'Standard', etc."
    )
    color: Optional[str] = Field(
        default=None, description="Specific color name or color family"
    )
    features: Optional[List[str]] = Field(
        default=None,
        description="Special features like 'washable', 'anti-mold', 'antimicrobial', etc.",
    )
    surface_types: Optional[List[str]] = Field(
        default=None,
        description="Compatible surface types like 'concrete', 'wood', 'metal', etc.",
    )
    limit: Optional[int] = Field(
        default=5, description="Maximum number of results to return"
    )


class PaintDetailsArgs(BaseModel):
    product_id: str = Field(description="Unique product identifier for the paint")


class PaintRecommendationAgent:
    def __init__(self):
        """Initialize the Paint Recommendation Agent"""
        self.llm = ChatOpenAI(
            api_key=config.OPENAI_API_KEY,
            model=config.OPENAI_MODEL,
            temperature=0.3,  # Lower temperature for more consistent recommendations
        )

        self.memory = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True
        )

        self.vector_store = get_vector_store()
        self._setup_agent()

    def _setup_agent(self):
        """Setup the LangChain agent with tools using modern approach"""
        tools = [
            StructuredTool.from_function(
                name="search_paints",
                description="Search for paint products based on user requirements like color, room type, or features",
                func=self._search_paints_tool,
                args_schema=PaintSearchArgs,
            ),
            StructuredTool.from_function(
                name="filter_paints",
                description="Filter paint products by specific attributes like environment (internal/external), finish type, or product line",
                func=self._filter_paints_tool,
                args_schema=PaintFilterArgs,
            ),
            StructuredTool.from_function(
                name="get_paint_details",
                description="Get detailed information about a specific paint product using its unique product ID",
                func=self._get_paint_details_tool,
                args_schema=PaintDetailsArgs,
            ),
        ]

        system_prompt = """You are an intelligent paint recommendation assistant for Suvinil paints. 
        You help customers find the perfect paint products based on their needs, preferences, and project requirements.
        
        Your capabilities:
        - Understand customer intent (room type, color preferences, project requirements)
        - Search for relevant paint products using semantic similarity
        - Filter products by specific attributes
        - Provide detailed product information and recommendations
        - Consider practical factors like environment, durability, and maintenance
        
        Guidelines:
        - Always be helpful and friendly
        - Ask clarifying questions when requirements are unclear
        - Recommend 2-3 products maximum unless asked for more
        - Explain why specific products are good matches
        - Consider both aesthetic and functional requirements
        - Respond in Portuguese (Brazilian) when the user speaks Portuguese
        - When recommending products, always include the product_id for future reference
        - Use the product_id from search/filter results when getting detailed information
        """

        prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(content=system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        # Create agent
        agent = create_openai_tools_agent(self.llm, tools, prompt)

        # Create AgentExecutor
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            memory=self.memory,
            verbose=True,
            max_iterations=3,
            return_intermediate_steps=True,
        )

    def _search_paints_tool(self, query: str, limit: Optional[int] = 5) -> str:
        """Search paint products using vector similarity"""
        try:
            results = self.vector_store.search(query, k=limit or 5)

            if not results:
                return "No paint products found matching your search criteria."

            # Format results for the agent
            formatted_results = []
            for i, product in enumerate(results, 1):

                product_id = (
                    str(product.get("id"))
                    or f"paint_{product['name'].lower().replace(' ', '_')}_{product['color'].lower().replace(' ', '_')}"
                )

                result_text = f"""
                {i}. {product['name']} - {product['color']}
                   Product ID: {product_id}
                   Line: {product['product_line']}
                   Environment: {product['environment']}
                   Finish: {product['finish_type']}
                   Price: R$ {product['price'] if product['price'] else 'N/A'}
                   Features: {', '.join(product['features']) if product['features'] else 'Standard'}
                   Summary: {product.get('ai_summary', 'No summary available')}
                """
                formatted_results.append(result_text.strip())

            return f"Found {len(results)} matching paint products:\n\n" + "\n\n".join(
                formatted_results
            )

        except Exception as e:
            logger.error(f"Error in search_paints_tool: {e}")
            return f"Error searching for paint products: {str(e)}"

    def _filter_paints_tool(
        self,
        environment: Optional[str] = None,
        finish_type: Optional[str] = None,
        product_line: Optional[str] = None,
        color: Optional[str] = None,
        features: Optional[List[str]] = None,
        surface_types: Optional[List[str]] = None,
        limit: Optional[int] = 5,
    ) -> str:
        """Filter paint products by attributes with structured arguments"""
        try:
            # Build filters dict from structured arguments
            filters = {}

            if environment:
                filters["environment"] = environment
            if finish_type:
                filters["finish_type"] = finish_type
            if product_line:
                filters["product_line"] = product_line
            if color:
                filters["color"] = color
            if features:
                filters["features"] = features
            if surface_types:
                filters["surface_types"] = surface_types

            if not filters:
                return "No filter criteria provided. Please specify at least one filter parameter."

            results = self.vector_store.search("", **filters)

            if not results:
                filter_summary = ", ".join([f"{k}: {v}" for k, v in filters.items()])
                return f"No paint products found with the specified filters: {filter_summary}"

            # Format results with product_id for future reference
            formatted_results = []
            for i, product in enumerate(results[: limit or 5], 1):
                product_id = (
                    str(product.get("id"))
                    or f"paint_{product['name'].lower().replace(' ', '_')}_{product['color'].lower().replace(' ', '_')}"
                )

                result_text = f"""
                {i}. {product['name']} - {product['color']}
                   Product ID: {product_id}
                   Line: {product['product_line']}
                   Environment: {product['environment']}
                   Finish: {product['finish_type']}
                   Price: R$ {product['price'] if product['price'] else 'N/A'}
                   Features: {', '.join(product['features']) if product['features'] else 'Standard'}
                """
                formatted_results.append(result_text.strip())

            filter_summary = ", ".join([f"{k}: {v}" for k, v in filters.items()])
            return (
                f"Found {len(results)} products matching filters ({filter_summary}):\n\n"
                + "\n\n".join(formatted_results)
            )

        except Exception as e:
            logger.error(f"Error in filter_paints_tool: {e}")
            return f"Error filtering paint products: {str(e)}"

    def _get_paint_details_tool(self, product_id: str) -> str:
        """Tool for getting detailed information about a specific paint using product ID"""
        try:
            from shared.database import get_db
            from shared.models import PaintProductModel as PaintProduct

            db = next(get_db())

            try:
                # Try to find by id first
                try:
                    product = (
                        db.query(PaintProduct)
                        .filter(PaintProduct.id == int(product_id))
                        .first()
                    )
                except ValueError:
                    product = None

                if not product and product_id.startswith("paint_"):
                    # Try to extract name and color from pattern
                    parts = (
                        product_id.replace("paint_", "").replace("_", " ").split(" ")
                    )
                    if len(parts) >= 2:
                        # Search for products matching the pattern
                        products = db.query(PaintProduct).all()
                        for p in products:
                            reconstructed_id = f"paint_{p.name.lower().replace(' ', '_')}_{p.color.lower().replace(' ', '_')}"
                            if reconstructed_id == product_id:
                                product = p
                                break

                if not product:
                    return f"Could not find product with ID: {product_id}. Please ensure you're using the correct product_id from search or filter results."

                # Format detailed product information
                details = f"""
                Detailed Information for {product.name}:
                
                Product ID: {product.id}
                Color: {product.color}
                Product Line: {product.product_line}
                Environment: {product.environment}
                Finish Type: {product.finish_type}
                Price: R$ {product.price if product.price else 'N/A'}
                
                Surface Types: {', '.join(product.surface_types) if product.surface_types else 'Standard surfaces'}
                Special Features: {', '.join(product.features) if product.features else 'Standard paint features'}
                Usage Tags: {', '.join(product.usage_tags) if product.usage_tags else 'General use'}
                
                AI Summary: {product.ai_summary or 'No detailed summary available'}
                
                Recommendation Notes:
                - Best suited for {product.environment} use
                - {product.finish_type.capitalize()} finish provides {'durability and easy cleaning' if 'washable' in (product.features or []) else 'excellent coverage'}
                - Compatible with: {', '.join(product.surface_types) if product.surface_types else 'most standard surfaces'}
                """

                return details.strip()

            finally:
                db.close()

        except Exception as e:
            logger.error(f"Error in get_paint_details_tool: {e}")
            return (
                f"Error getting paint details for product_id '{product_id}': {str(e)}"
            )

    def get_recommendation(self, user_query: str) -> str:
        """Get paint recommendation based on user query"""
        try:
            result = self.agent_executor.invoke({"input": user_query})
            return result["output"]

        except Exception as e:
            logger.error(f"Error getting recommendation: {e}")
            return (
                f"Sorry, I encountered an error while processing your request: {str(e)}"
            )

    def reset_conversation(self):
        """Reset the conversation memory"""
        self.memory.clear()
        logger.info("Conversation memory reset")


# Global agent instance
paint_agent = PaintRecommendationAgent()


def get_paint_agent() -> PaintRecommendationAgent:
    """Get the global paint recommendation agent"""
    return paint_agent
