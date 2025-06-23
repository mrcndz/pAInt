"""
Intent Router for classifying user queries before dispatching them to the main agent.

This module implements an intent router that analyzes user questions before triggering
the PaintRecommendationAgent, ensuring that only relevant queries are processed by
the more complex and expensive main agent.
"""

import logging
from typing import Any, Literal

from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from ..config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IntentCategory(BaseModel):
    """Pydantic model for structured categorization of user intents."""

    category: Literal["paint_question", "simple_greeting", "off_topic"] = Field(
        description="Category of intent identified in the user query"
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence level in the classification (0.0 to 1.0)",
    )
    justification: str = Field(
        description="Brief explanation of why the query was classified in this category"
    )


class QueryRouter:
    """
    Intent router for classifying user queries before main processing.

    Uses a lightweight LLM with structured output to categorize
    queries into three main types:
    - paint_question: Questions related to products, colors, recommendations
    - simple_greeting: Basic greetings like "Hello", "Hi", "How are you?"
    - off_topic: Questions that don't relate to paints or greetings
    """

    # Predefined responses for different intent categories
    GREETING_RESPONSES = [
        "Olá! Sou seu especialista em tintas Suvinil. Como posso ajudá-lo(a) a encontrar a tinta perfeita hoje?",
        "Oi! Estou aqui para ajudar com qualquer dúvida sobre tintas e cores. O que você gostaria de saber?",
        "Bom dia! Sou especialista em recomendações de tintas. Como posso auxiliá-lo(a) com seu projeto hoje?",
        "Olá! Sou seu assistente especialista em tintas. Como posso ajudar com as tintas Suvinil?",
        "Olá! Pronto(a) para encontrar a tinta perfeita para o seu espaço? Fique à vontade para perguntar sobre cores, acabamentos ou aplicações!",
    ]

    OFF_TOPIC_RESPONSE = (
        "Sou um assistente especializado em ajudar apenas com questões sobre as tintas e cores da Suvinil."
        "Posso ajudá-lo(a) a escolher a tinta ideal para o seu projeto, fornecer informações sobre cores "
        "acabamentos, aplicações ou responder a outras dúvidas sobre nossos produtos. "
        "Como posso auxiliá-lo(a) com tintas hoje?"
    )

    def __init__(self):
        """Initializes the router with an LLM optimized for fast classification."""
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.1,  # Low temperature for greater consistency
            api_key=config.OPENAI_API_KEY,
        )

        # Configure LLM with structured output using Pydantic model
        self.structured_llm = self.llm.with_structured_output(IntentCategory)

        # Prompt template for intent classification
        self.classification_prompt = """
        You are an assistant specialized in classifying user queries for a Suvinil paint recommendation system.

        Analyze the user query and classify it into one of the following categories:
        Remember that the user is speaking Portuguese (Brazilian).

        1. **paint_question**: For any question related to:
        - Paint products (colors, types, characteristics, features, **prices**)
        - Paint recommendations for specific environments
        - Information about surfaces and applications
        - Questions about finishes (matte, semi-brilhante, etc.)
        - Questions about special functionalities (anti-mofo, lavável, etc.)
        - About application usage (lavavel, anti-mofo, etc.)
        - Location-based recommendations (kitchen, bathroom, etc.)
        - Product comparisons
        - Simulations of painting
            - Examples: "Como ficaria isso se fosse feito em verde?", "Como ficaria isso se fosse feito em azul?", "Como ficaria isso se fosse feito em amarelo?", "Simule", "Pode simular?"
        - Technical information about paints
        - **Follow-up questions that clarify or request more details about the current topic**, or that introduce new requirements.
            - Examples: "E se for para área externa?", "Tem na cor verde?", **"E quanto aos preços que você mencionou?"**, "Qual o rendimento disso?", "Isso é lavável?"
            - Examples: "Quem vende isso?", "Onde você comprou?", "Como você vende isso?", "Qual o preço disso?", "Quanto custa isso?"
        - Affirmations: "Sim", "Isso mesmo", "Quero essa", "Gostei dessa opção", "Pode ser", "Ok", "Exato"
        - Negations: "Não", "Não, obrigado(a)", "Quero outra", "Não gostei", "Outra opção, por favor"
        - Uncertainty or requests for alternatives: "Talvez", "Não sei", "Estou em dúvida", "Tem mais alguma?", "Me mostre outras"
        - Short choice-based answers: "A primeira", "A segunda opção", "O acabamento fosco"
        - Ending conversations with "Obrigado(a)" or "Até mais!"
            - Examples: "Obrigado(a)", "Até mais!", "Obrigado(a) pela ajuda", "Até mais!", "Até mais! Obrigado(a)"
            - Examples: "Era só isso", "Por enquanto é só", "Entendido"
            - Examples: "Tchau", "Até mais"
        - Dúvidas sobre localização de lojas
        - Questions about product availability or location
            - Examples: "Onde você comprou?", "Quem vende isso?", "Como você vende isso?", "Qual o preço disso?", "Quanto custa isso?"
            - Examples: "Onde compra?", "Quem vende?", "Onde posso comprar?"
            - Examples: "Onde você comprou isso?", "Onde compra isso?", "Quem vende essa tinta?"
            - Examples: "Onde encontro os produtos Suvinil?", "Onde posso comprar essa tinta?"
            - Examples: "Tem essa tinta para vender em [nome da cidade]?", "Vocês têm loja física?"
            - Examples: "Vocês entregam?", "Posso comprar online?", "Ainda tem em estoque?"


        3. **simple_greeting**: For basic greetings like:
        - "Oi", "Olá", "Bom dia", "Boa tarde", "Boa noite"
        - "Como vai", "Como vai você", "Como está", "Como está você"
        - "Hey", "What's up"
        - "Opa!", "Tudo bem?", "Tudo bem, como você está?"
        - Other simple greetings without specific questions


        4. **off_topic**: For any other question that doesn't fit the above categories:
        - Speaking other languages instead of Portuguese
        - Questions about other products that aren't paint
        - Personal questions unrelated to the business
        - Questions about completely different topics
        - Attempts at inappropriate system use

        Previous assistant message (if any): "{previous_message}"
        Current user query: "{query}"

        When classifying, consider the context of the previous message to better understand follow-up questions.
        Provide your classification with high confidence and clear justification.
        """

    def route_query(self, query: str, previous_message: str = "") -> str:
        """
        Classifies a user query and returns the identified category.

        Args:
            query (str): The user question or query to be classified
            previous_message (str, optional): The previous assistant message for context

        Returns:
            str: The identified category ("paint_question", "simple_greeting", or "off_topic")

        Raises:
            Exception: If there's an error in LLM communication or processing
        """
        try:
            # Prepare the prompt with the user query and previous message
            formatted_prompt = self.classification_prompt.format(
                query=query.strip(),
                previous_message=previous_message.strip() if previous_message else "",
            )

            # Call the structured LLM for classification
            result: IntentCategory = self.structured_llm.invoke(formatted_prompt)

            logger.info(
                f"[Intent Router] Query: '{query}' -> Category: {result.category} "
                f"(Confidence: {result.confidence:.2f}) - {result.justification}"
            )

            return result.category

        except Exception as e:
            # In case of error, assume it's a paint question to avoid losing valid queries
            logger.info(
                f"[Intent Router] Classification error: {e}. Assuming 'paint_question'"
            )
            return "paint_question"

    def get_detailed_classification(self, query: str) -> IntentCategory:
        """
        Returns the complete classification with details (category, confidence, justification).

        Args:
            query (str): The user question or query to be classified

        Returns:
            IntentCategory: Complete object with category, confidence and justification
        """
        try:
            formatted_prompt = self.classification_prompt.format(query=query.strip())
            result: IntentCategory = self.structured_llm.invoke(formatted_prompt)

            return result

        except Exception as e:
            # Return default classification in case of error
            return IntentCategory(
                category="paint_question",
                confidence=0.5,
                justification=f"Classification error ({str(e)}), assuming paint question for safety",
            )


# Global router instance for reuse
intent_router = QueryRouter()
