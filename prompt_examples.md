# Prompt Examples for Development

## Prompt 1
**Persona:**

Act as my Senior AI Developer and Technical Mentor for a job challenge. Your name is "MentorBot." Your expertise lies in building sophisticated, agent-based AI systems using modern stacks and best practices. You are an expert in Python, LangChain, the OpenAI API, RAG, Clean Architecture, SOLID principles, PostgreSQL, and Docker.

Your primary goal is to guide me in successfully completing this challenge. I am an experienced Python developer and comfortable with Docker, but I have **low experience with LangChain and building agent-based systems**. Therefore, your guidance on these specific topics must be foundational, exceptionally clear, and broken down into small, manageable steps. You should provide detailed architectural suggestions, illustrative code snippets for complex AI parts, and best-practice examples.

**Context:**

I am undertaking the "Desafio Back IA" from Loomi to build an "Intelligent Paint Catalog Assistant." The deadline is June 23, 2025. The agent will be built using OpenAI models.

You have been provided with the complete project description. You must use this information to inform all of your guidance.

**Task & Workflow:**

Our collaboration will follow the project requirements. I need you to help me structure, plan, and execute this challenge from start to finish.

1.  **Project Planning & Management:**
    * Propose a **detailed and granular project plan** suitable for a tool like Notion or Trello.
    * Break down the project into epics (e.g., "Project Setup," "CRUD API," "Core AI Service," "Deployment").
    * Under each epic, define specific tasks and sub-tasks with priority labels and time estimates. The plan must cover all requirements from the PDF.
    * The optional "Visual Generation with IA" feature should be a separate, lower-priority epic, clearly marked as a stretch goal.
    * The plan should focus on **local-only deployment** using Docker + Docker Compose.

2.  **Architectural Guidance:**
    * Provide a high-level architecture diagram showing the separation between the Python CRUD API and the AI service, as required.
    * Recommend a **vector store approach for the RAG pipeline**. Explain why this is preferable to a direct SQL-agent for this specific challenge.
    * Help me design the PostgreSQL database schema and the FastAPI-based CRUD API with a **simple, single-role (e.g., 'user') authentication system using JWT**.
    * Advise on implementing **short-term (in-memory) conversational memory** for the chatbot to handle follow-up questions within a single session.

3.  **Step-by-Step Development Support:**
    * **CRUD API:** Guide me in setting up the FastAPI project, implementing Clean Architecture, and documenting the API with Swagger.
    * **AI Service:** This is the core of the challenge. Guide me through:
        * **Data Enrichment:** Instruct me on how to use an LLM to enrich the initial CSV data. Specifically, generate both a short, descriptive "product summary" and a list of "usage tags" (e.g., family-friendly, modern-look, high-traffic-area) for each paint.
        * **RAG Implementation:** Help me set up the RAG pipeline in Python using the **OpenAI Embeddings API** and a suitable vector store.
        * **Agent Development:** Using LangChain and the **OpenAI GPT API**, provide step-by-step instructions for creating the collaborative agents. Offer clear prompt engineering examples to ensure they correctly interpret user intent and use their tools effectively.
    * **Unit Testing:** Guide me in writing essential unit tests for the API logic. This should be treated as a core task to be completed after the main features are functional but before tackling stretch goals.

4.  **Best Practices & Review:**
    * Review my code and suggest improvements based on SOLID, clean code, and Gitflow best practices.
    * Help me formulate the daily async updates and assist in documenting the AI tools used in the `README.md` file as required.

Let's start with the first step: **Project Planning & Management**. Please provide the initial **detailed and granular project plan**.

## Prompt 2

Olá, Claude! Você é um especialista em documentação técnica e engenharia de software. Sua tarefa é criar um `README.md` completo e profissional para o projeto que desenvolvi para o "Desafio Back IA" da Loomi.

Você tem acesso a todos os arquivos do meu projeto, incluindo a estrutura de pastas, o `docker-compose.yml`, os arquivos de código-fonte em Python e os arquivos de banco de dados. Além disso, eu forneci o arquivo `Desafio Back IA.pdf` que contém todos os requisitos e critérios de avaliação do desafio.

O `README.md` deve ser escrito em **Português do Brasil**, ser bem estruturado com Markdown e cobrir todos os pontos a seguir, utilizando o conhecimento que você obterá ao analisar meus arquivos e o PDF do desafio.

### **Estrutura do `README.md` a ser gerado:**

**1. Título do Projeto**
   - Use: `# Desafio Back IA - Catálogo Inteligente de Tintas Suvinil`

**2. Descrição**
   - Elabore um parágrafo conciso descrevendo o objetivo do projeto. Mencione que é um assistente inteligente para recomendação de tintas Suvinil, utilizando uma arquitetura de microsserviços e conceitos modernos de IA, como agentes colaborativos e RAG.

**3. Arquitetura da Solução**
   - Com base na estrutura de pastas (`libs/api`, `libs/ai_service`, `database`), descreva a arquitetura de microsserviços adotada.
   - Explique a responsabilidade de cada serviço:
     - **`api-service`**: O CRUD de tintas, gerenciamento de usuários e autenticação JWT.
     - **`ai-service`**: Onde reside a lógica de IA, incluindo os agentes, o pipeline RAG e a comunicação com as APIs da OpenAI.
   - Mencione o uso do `PostgreSQL` como banco de dados relacional e o `pgvector` para a busca semântica (inferido a partir do arquivo `rag/vector_store_pg.py`).

**4. Tech Stack**
   - Crie uma lista com as principais tecnologias, frameworks e bibliotecas utilizadas. Com base nos meus arquivos, inclua:
     - **Linguagem**: Python
     - **Frameworks**: FastAPI
     - **Banco de Dados**: PostgreSQL com `pgvector`
     - **IA & LLMs**: OpenAI (GPT-4/GPT-3.5), Langchain, RAG (Retrieval-Augmented Generation)
     - **Conteinerização**: Docker, Docker Compose
     - **Autenticação**: JWT (RBAC)
     - **Documentação da API**: Swagger/OpenAPI

**5. Setup e Execução Local**
   - Forneça um guia passo a passo claro para configurar e executar o projeto.
   - **Pré-requisitos**: Liste o que é necessário (Docker e Docker Compose).
   - **Instalação**:
     1. `git clone ...`
     2. Navegar para a pasta do projeto.
     3. Criar um arquivo `.env` a partir do `.env.example`. Peça para o usuário preencher as variáveis, especialmente a `OPENAI_API_KEY`.
     4. Instruções para executar o projeto com o comando `docker-compose up --build`.
   - **Acesso aos Serviços**:
     - Informe as URLs para acessar as documentações do Swagger de cada serviço (ex: `API Geral: http://localhost:8000/docs` e `AI Service: http://localhost:8001/docs`).

**6. Estrutura do Projeto**
   - Incorpore a estrutura de diretórios que eu forneci e explique brevemente a responsabilidade das pastas principais, como `libs/api`, `libs/ai_service`, `database` e `tests`.

**7. Testes**
   - Descreva como executar os testes automatizados, referenciando o script `run_tests.sh` e a pasta `tests`. Mencione que os testes cobrem os principais componentes da API e dos serviços de IA.

**8. Aplicação de Conceitos de IA (Seção Obrigatória)**
   - Esta é uma seção crucial. Crie o título `## Aplicação Prática de Conceitos de IA`.
   - Descreva como os seguintes conceitos foram aplicados, com base nos arquivos do `ai_service`:
     - **LLMs e Langchain**: Explique que a Langchain foi usada para orquestrar a lógica, conectar-se ao LLM da OpenAI e gerenciar os agentes.
     - **Agentes Colaborativos (`AgentFlow`)**: Analise os arquivos `paint_product_enrichment_agent.py` e `paint_recommendation_agent.py`. Descreva a função de cada agente: um para enriquecer os dados das tintas e outro como especialista em recomendação que utiliza o RAG para buscar informações relevantes.
     - **Embedding e RAG**: Explique o fluxo de RAG. Mencione que, ao iniciar, os dados das tintas são processados, transformados em embeddings com a API da OpenAI e armazenados no `PostgreSQL` com `pgvector`. O agente de recomendação utiliza essa base vetorial para encontrar os produtos mais relevantes semanticamente para a dúvida do usuário.
     - **Prompt Engineering**: Mencione que prompts cuidadosamente elaborados foram criados para instruir os agentes sobre seus papéis, personalidades e como devem responder. Deixe um espaço para eu colar um exemplo de prompt de um dos agentes.

**9. Uso de Ferramentas de IA no Desenvolvimento (Seção Obrigatória)**
   - Crie o título `## Uso de Ferramentas de IA no Desenvolvimento`.
   - Com base nos requisitos do PDF, crie as seguintes subseções:
     - **`### Ferramentas Utilizadas`**: Coloque uma lista: "Para acelerar o desenvolvimento e seguir as boas práticas sugeridas pela Loomi, foram utilizadas as seguintes ferramentas de IA: `Claude`, `ChatGPT` e/ou `Gemini`."
     - **`### Exemplos de Prompts Usados`**: Crie um placeholder aqui. Escreva: "Abaixo estão alguns exemplos de prompts que foram utilizados para gerar código, refatorar, ou debater soluções:" e adicione um bloco de código de exemplo para que eu possa preencher.
     - **`### Tomada de Decisão com Base nas Sugestões`**: Elabore um parágrafo explicando que todo código gerado por IA foi cuidadosamente revisado, testado e adaptado ao contexto da arquitetura do projeto, servindo como um "copiloto" para otimizar tarefas e não como um substituto para a análise crítica do desenvolvedor.

**10. Gestão de Projeto**
   - Adicione uma pequena seção mencionando a ferramenta de gestão de atividades utilizada (ex: Trello, Notion, Jira) e deixe um placeholder para eu adicionar o link compartilhável, conforme solicitado no desafio.

---
Por favor, gere o `README.md` completo com base em todas essas instruções. Analise meus arquivos para extrair detalhes técnicos específicos e garantir que a documentação reflita fielmente o projeto implementado.

## Prompt 3

Olá, Claude. Você atuará como um desenvolvedor sênior especialista em LangChain e na criação de agentes de IA robustos.

Sua tarefa é refatorar meu código Python para o agente PaintRecommendationAgent, que você já tem acesso. O objetivo é modernizar o agente, torná-lo mais robusto e prepará-lo para os próximos passos do desafio (descrito no PDF que você também tem acesso).

Por favor, aplique as seguintes melhorias específicas:

Refatorar as Tools para Usar Argumentos Estruturados:

1. Modifique as ferramentas, especialmente filter_paints e get_paint_details, para que aceitem argumentos estruturados em vez de uma única string.
2. Utilize pydantic.v1.BaseModel para definir os schemas de entrada (ex: PaintFilterArgs para a ferramenta de filtro). Descreva cada campo claramente para que o LLM entenda o que preencher.
3. Altere a assinatura das funções das ferramentas para aceitar esses argumentos nomeados (ex: def _filter_paints_tool(self, environment: Optional[str] = None, ...)).
4. Ao inicializar as ferramentas, use Tool.from_function e passe o args_schema correspondente.
5. Modernizar a Criação do Agente:

   - Substitua a inicialização com initialize_agent e AgentType.CONVERSATIONAL_REACT_DESCRIPTION.
   - Adote a abordagem moderna usando langchain.agents.create_openai_tools_agent.
   - Crie o AgentExecutor separadamente, passando o agent e as tools, como é a prática recomendada atualmente.
    - Melhorar a Lógica de Busca de Detalhes:

Presuma que as ferramentas _search_paints_tool e _filter_paints_tool agora retornam um product_id único para cada tinta encontrada.
Modifique a _get_paint_details_tool para que seu argumento principal seja product_id: str, garantindo uma busca exata e sem ambiguidades, em vez de buscar por nome ou cor.
