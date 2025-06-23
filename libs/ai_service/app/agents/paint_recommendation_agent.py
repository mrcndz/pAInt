import base64
import logging
from typing import List, Optional

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import StructuredTool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from ..config import config
from ..rag.vector_store_pg import get_vector_store
from ..services.conversation_manager import ConversationManager
from ..services.inpainting_service import simulate_paint_on_image

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
        description="Environment type: 'interno' for indoor use or 'externo' for outdoor use",
    )
    finish_type: Optional[str] = Field(
        default=None, description="Finish type: 'fosco', 'acetinado', 'brilhante', etc."
    )
    product_line: Optional[str] = Field(
        default=None, description="Product line: 'Premium', 'Padrão', etc."
    )
    color: Optional[str] = Field(
        default=None, description="Specific color name or color family"
    )
    features: Optional[List[str]] = Field(
        default=None,
        description="Special features like 'lavável', 'antimofo', 'antimicrobiano', etc.",
    )
    surface_types: Optional[List[str]] = Field(
        default=None,
        description="Compatible surface types like 'parede', 'teto', 'madeira', 'metal', etc.",
    )
    limit: Optional[int] = Field(
        default=5, description="Maximum number of results to return"
    )


class PaintDetailsArgs(BaseModel):
    product_id: str = Field(description="Unique product identifier for the paint")


class PaintSimulationArgs(BaseModel):
    image_base64: str = Field(
        description="Use 'USER_IMAGE' to reference the uploaded image"
    )
    paint_description: str = Field(
        description="Description of the paint color/product to simulate"
    )


class PaintRecommendationAgent:
    """
    Session-aware paint recommendation agent that uses ConversationManager
    for persistent conversation memory across sessions.
    """

    def __init__(self, conversation_manager: ConversationManager):
        """Initialize the Session-Aware Paint Recommendation Agent"""
        self.llm = ChatOpenAI(
            api_key=config.OPENAI_API_KEY,
            model=config.OPENAI_MODEL,
            temperature=0.3,  # Lower temperature for more consistent recommendations
        )

        self.conversation_manager = conversation_manager
        self.vector_store = get_vector_store()
        self.current_image_data = None  # Store image data for the session
        self._setup_tools()
        self._setup_prompt_template()

    def _setup_tools(self):
        """Setup the tools for the agent"""
        self.tools = [
            StructuredTool.from_function(
                name="search_paints",
                description="Search for paint products based on user requirements like color, room type, or features",
                func=self._search_paints_tool,
                args_schema=PaintSearchArgs,
            ),
            StructuredTool.from_function(
                name="filter_paints",
                description="Filter paint products by specific attributes like environment (interno/externo), finish type, or product line",
                func=self._filter_paints_tool,
                args_schema=PaintFilterArgs,
            ),
            StructuredTool.from_function(
                name="get_paint_details",
                description="Get detailed information about a specific paint product using its unique product ID",
                func=self._get_paint_details_tool,
                args_schema=PaintDetailsArgs,
            ),
            StructuredTool.from_function(
                name="simulate_paint",
                description="Simulate a paint color on the user's uploaded image. Use this when the user has uploaded an image and wants to see how a specific paint would look on it. Always use 'USER_IMAGE' as the image_base64 parameter - the system will automatically use the uploaded image.",
                func=self._simulate_paint_tool,
                args_schema=PaintSimulationArgs,
            ),
        ]

    def _setup_prompt_template(self):
        """Setup the prompt template for the agent"""
        system_prompt = """You are an intelligent paint recommendation assistant for Suvinil paints. 
        You help customers find the perfect paint products based on their needs, preferences, and project requirements.

        Key Responsibilities:
        - Understand customer requirements through natural conversation
        - Search and recommend appropriate paint products using available tools
        - Provide detailed product information including prices, features, and usage recommendations
        - Maintain conversation context to provide personalized recommendations
        - Answer questions in Portuguese (primary) or English as appropriate

        Guidelines:
        - Always be helpful, professional, and enthusiastic about paint projects
        - Ask clarifying questions when requirements are unclear
        - Recommend specific products with prices when possible
        - Consider factors like room type, lighting, usage patterns, and maintenance needs
        - Explain the reasoning behind your recommendations
        - Use the search and filter tools effectively to find the best matches
        - Remember previous conversation context to provide continuous assistance
        - When users provide images, use the simulate_paint tool to show them how recommended paints would look
        - Only use paint simulation when both an image and a specific paint color/product are available
        - The image data is stored separately and accessed via tools - never include actual image data in conversations
        - If the user expresses gratitude (e.g., "obrigado", "valeu", "ficou lindo!"), respond politely acknowledging their thanks and offering further assistance. For example: "De nada! Se precisar de mais alguma coisa sobre tintas, é só perguntar."

        Available Product Information:
        - Suvinil paint products with various colors, finishes, and features
        - Price information in Brazilian Reais (BRL)
        - Surface compatibility (parede, teto, madeira, metal, etc.)
        - Environmental suitability (interno, externo)
        - Special features (lavável, antimofo, secagem rápida, etc.)
        - Product lines (Premium, Padrão, Econômico, Especial)

        The products are available to buy in Suvinil's online or physical store if asked.

        Remember: You have access to search_paints, filter_paints, get_paint_details, and simulate_paint tools to help customers find exactly what they need and visualize the results.
        """

        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                SystemMessage(content=system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

    def get_recommendation(
        self,
        message: str,
        session_uuid: str,
        user_id: int,
        image_base64: Optional[str] = None,
    ) -> dict:
        """
        Get paint recommendation for a specific session.

        Args:
            message: User's message/query
            session_uuid: Session UUID for conversation tracking
            user_id: User ID for session ownership
            image_base64: Optional base64 encoded image for paint simulation

        Returns:
            Dict containing response text and optional image data
        """
        # Store image data for potential use in tools
        if image_base64:
            self.current_image_data = image_base64
            # Add minimal context about image without including the actual data
            image_info = f"[IMAGEM RECEBIDA - {len(image_base64)//1000}KB] {message}"
            message = image_info

        # Get session-specific memory
        memory = self.conversation_manager.get_memory_for_session(session_uuid, user_id)

        try:
            logger.info(
                f"Processing recommendation for session {session_uuid}, user {user_id}"
            )

            # Create agent executor with session-specific memory
            agent_executor = AgentExecutor(
                agent=create_openai_tools_agent(
                    llm=self.llm,
                    tools=self.tools,
                    prompt=self.prompt_template,
                ),
                tools=self.tools,
                memory=memory,
                verbose=True,
                handle_parsing_errors=True,
                max_iterations=config.AGENT_MAX_ITERATIONS,
                max_execution_time=config.AGENT_MAX_EXECUTION_TIME,
            )

            # Execute the agent
            response = agent_executor.invoke({"input": message})

            # Save updated conversation to database
            self.conversation_manager.save_session_to_database(
                session_uuid, user_id, memory
            )

            logger.info(
                f"Successfully processed recommendation for session {session_uuid}"
            )

            # Check if response indicates max iterations reached but we have an image
            response_text = response.get("output", "")
            result = {"response": response_text}

            if hasattr(self, "_generated_image"):
                result["image_data"] = self._generated_image
                # Override the error message if we successfully generated an image
                if "Agent stopped due to max iterations" in response_text:
                    result["response"] = (
                        "Simulação de pintura concluída com sucesso! A imagem foi gerada e está sendo retornada para visualização."
                    )
                delattr(self, "_generated_image")

            return result

        except Exception as e:
            logger.error(f"Error in get_recommendation: {e}")

            # Handle specific max iterations error
            if "max iterations" in str(e).lower() or "agent stopped" in str(e).lower():
                # Still save conversation if we have valid memory
                try:
                    self.conversation_manager.save_session_to_database(
                        session_uuid, user_id, memory
                    )
                except:
                    pass

                # Check if we have a generated image despite the error
                result = {"response": ""}
                if hasattr(self, "_generated_image"):
                    result["image_data"] = self._generated_image
                    result["response"] = (
                        "Simulação de pintura concluída com sucesso! A imagem foi gerada e está sendo retornada para visualização."
                    )
                    delattr(self, "_generated_image")
                    return result

                return {
                    "response": (
                        "Sua consulta é muito detalhada e preciso de mais tempo para processar. "
                        "Vou te ajudar de forma mais direta:\n\n"
                        "• Para recomendações gerais: 'Quero tinta azul para sala'\n"
                        "• Para características específicas: 'Preciso tinta lavável para cozinha'\n"
                        "• Para simulação: Envie uma foto e diga 'Como ficaria em verde?'\n\n"
                        "Qual dessas opções se encaixa melhor no que você precisa?"
                    )
                }

            return {
                "response": f"Desculpe, ocorreu um erro ao processar sua solicitação. Erro: {str(e)}"
            }

    def _translate_to_english(self, paint_description: str) -> str:
        """
        Translate paint description to English using GPT.
        StabilityAI only supports English, so we use GPT to translate the description to English.
        """
        try:
            prompt = f"Translate this paint color description to simple English for an AI image generator. Only return the English translation, nothing else: '{paint_description}'"

            response = self.llm.invoke(prompt)
            content = response.content

            if content is None:
                raise ValueError("Empty response from the LLM")

            actual_text = ""
            # Verifies if the response is a string or a list of strings
            if isinstance(content, str):
                actual_text = content
            elif isinstance(content, list):
                if len(content) > 0 and isinstance(content[0], str):
                    actual_text = content[0]
                else:
                    raise TypeError(
                        f"Response content is a list but its first element is not a string. Content: {content}"
                    )
            else:
                raise TypeError(
                    f"Unexpected response content type: {type(content)}. Content: {content}"
                )

            english_translation = actual_text.strip().replace('"', "").replace("'", "")

            logger.info(f"Translated '{paint_description}' to '{english_translation}'")
            return english_translation
        except Exception as e:
            logger.warning(
                f"Translation failed: {e}, using original: {paint_description}"
            )
            return paint_description

    def _simulate_paint_tool(self, image_base64: str, paint_description: str) -> str:
        """Tool for simulating paint on an image"""
        try:
            logger.info(f"Simulating paint: {paint_description}")

            # Always use current session image (ignore the placeholder parameter)
            image_to_use = self.current_image_data

            if not image_to_use:
                return "Erro: Nenhuma imagem disponível para simulação. O usuário precisa fornecer uma imagem."

            # Clean and validate base64 string
            try:
                import base64
                import re

                # Remove any non-ASCII characters and whitespace
                image_to_use = re.sub(r"[^\x00-\x7F]+", "", image_to_use)
                image_to_use = image_to_use.strip()

                # Remove data URL prefix if present
                if "," in image_to_use:
                    image_to_use = image_to_use.split(",")[1]

                # Validate base64 format
                base64.b64decode(image_to_use, validate=True)

            except Exception as e:
                return f"Erro: Imagem base64 inválida ou corrompida. {str(e)}"

            # Translate paint description to English for Stability AI
            english_prompt = self._translate_to_english(paint_description)

            # Call the inpainting service synchronously using a thread
            import asyncio
            import concurrent.futures
            import threading

            def run_async_in_thread():
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    return new_loop.run_until_complete(
                        simulate_paint_on_image(image_to_use, english_prompt)
                    )
                finally:
                    new_loop.close()

            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(run_async_in_thread)
                result_bytes = future.result()

            # Convert result to base64 for storage
            result_base64 = base64.b64encode(result_bytes).decode("utf-8")
            self._generated_image = result_base64

            return f"Simulação de pintura concluída com sucesso! A imagem foi gerada mostrando como ficaria a parede com '{paint_description}'. A imagem simulada está sendo retornada para visualização."

        except Exception as e:
            logger.error(f"Error in paint simulation tool: {e}")
            return f"Erro na simulação de pintura: {str(e)}"

    def _search_paints_tool(self, query: str, limit: int = 5) -> str:
        """Tool for semantic search of paint products"""
        try:
            logger.info(f"Searching paints with query: {query}")
            results = self.vector_store.search(query=query, k=limit)

            if not results:
                return "Nenhum produto encontrado para essa consulta."

            # Format results for the agent
            formatted_results = []
            for result in results:
                product_info = f"""
                ID: {result['id']}
                Nome: {result['name']}
                Cor: {result['color']}
                Linha: {result['product_line']}
                Ambiente: {result['environment']}
                Acabamento: {result['finish_type']}
                Preço: R$ {result.get('price', 'N/A')}
                Características: {', '.join(result.get('features', []))}
                Superfícies: {', '.join(result.get('surface_types', []))}
                Resumo: {result.get('ai_summary', 'N/A')}
                Score de relevância: {result.get('relevance_score', 0):.2f}
                """
                formatted_results.append(product_info.strip())

            return f"Encontrados {len(results)} produtos:\n\n" + "\n---\n".join(
                formatted_results
            )

        except Exception as e:
            logger.error(f"Error in search tool: {e}")
            return f"Erro na busca: {str(e)}"

    def _filter_paints_tool(
        self,
        environment: Optional[str] = None,
        finish_type: Optional[str] = None,
        product_line: Optional[str] = None,
        color: Optional[str] = None,
        features: Optional[List[str]] = None,
        surface_types: Optional[List[str]] = None,
        limit: int = 5,
    ) -> str:
        """Tool for filtering paint products by attributes"""
        try:
            logger.info(
                f"Filtering paints with filters: env={environment}, finish={finish_type}, line={product_line}"
            )

            # Build filter kwargs
            filter_kwargs = {}
            if environment:
                filter_kwargs["environment"] = environment
            if finish_type:
                filter_kwargs["finish_type"] = finish_type
            if product_line:
                filter_kwargs["product_line"] = product_line
            if color:
                filter_kwargs["color"] = color
            if features:
                filter_kwargs["features"] = features
            if surface_types:
                filter_kwargs["surface_types"] = surface_types

            results = self.vector_store.search(query="", k=limit, **filter_kwargs)

            if not results:
                return "Nenhum produto encontrado com os filtros especificados."

            # Format results
            formatted_results = []
            for result in results:
                product_info = f"""
                ID: {result['id']}
                Nome: {result['name']}
                Cor: {result['color']}
                Linha: {result['product_line']}
                Ambiente: {result['environment']}
                Acabamento: {result['finish_type']}
                Preço: R$ {result.get('price', 'N/A')}
                Características: {', '.join(result.get('features', []))}
                Superfícies: {', '.join(result.get('surface_types', []))}
                """
                formatted_results.append(product_info.strip())

            return (
                f"Encontrados {len(results)} produtos com os filtros aplicados:\n\n"
                + "\n---\n".join(formatted_results)
            )

        except Exception as e:
            logger.error(f"Error in filter tool: {e}")
            return f"Erro no filtro: {str(e)}"

    def _get_paint_details_tool(self, product_id: str) -> str:
        """Tool for getting detailed information about a specific paint product"""
        try:
            logger.info(f"Getting details for product ID: {product_id}")
            # Implementation would get product by ID from vector store
            # For now, return a placeholder
            return f"Detalhes do produto ID {product_id} serão implementados em breve."
        except Exception as e:
            logger.error(f"Error getting product details: {e}")
            return f"Erro ao obter detalhes do produto: {str(e)}"


def create_session_recommendation_agent(
    conversation_manager: ConversationManager,
) -> PaintRecommendationAgent:
    """Factory function to create a session-aware paint agent"""
    return PaintRecommendationAgent(conversation_manager)
