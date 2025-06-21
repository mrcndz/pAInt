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

        Available Product Information:
        - Suvinil paint products with various colors, finishes, and features
        - Price information in Brazilian Reais (BRL)
        - Surface compatibility (walls, ceilings, wood, metal, etc.)
        - Environmental suitability (internal/external use)
        - Special features (washable, anti-mold, quick-dry, etc.)
        - Product lines (Premium, Standard, Economy, Specialty)

        Remember: You have access to search_paints, filter_paints, and get_paint_details tools to help customers find exactly what they need.
        """

        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                SystemMessage(content=system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

    def get_recommendation(self, message: str, session_uuid: str, user_id: int) -> str:
        """
        Get paint recommendation for a specific session.

        Args:
            message: User's message/query
            session_uuid: Session UUID for conversation tracking
            user_id: User ID for session ownership

        Returns:
            AI-generated recommendation response
        """
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
                max_iterations=6,
                max_execution_time=30,
                early_stopping_method="generate",  # Stop and generate response if max iterations reached
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
            return response["output"]

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

                return (
                    "Desculpe, sua pergunta requer uma análise mais complexa do que posso processar no momento. "
                    "Pode reformular sua pergunta de forma mais específica? Por exemplo: 'Quero tinta azul para quarto' "
                    "ou 'Preciso de tinta lavável para cozinha'."
                )

            return f"Desculpe, ocorreu um erro ao processar sua solicitação. Erro: {str(e)}"

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
