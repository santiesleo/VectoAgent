# Módulo principal del agente con LangChain 1.x (API nueva basada en LangGraph)
# create_agent reemplaza a AgentExecutor + create_react_agent en esta versión

import os

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_core.tools.retriever import create_retriever_tool
from langchain_google_genai import ChatGoogleGenerativeAI

from src.mcp_client import get_mcp_tools


def build_agent(retriever):
    """
    Construye y retorna un agente compilado con la nueva API de LangChain 1.x.

    Usa Gemini 2.5 Flash como LLM y el retriever de ChromaDB como herramienta.
    LangSmith se activa automáticamente si LANGCHAIN_TRACING_V2=true está en el entorno.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY no encontrada. "
            "Asegúrate de configurarla en el archivo .env"
        )

    # Configurar el LLM: Gemini 2.5 Flash con temperatura 0
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
        google_api_key=api_key,
    )

    # Crear la herramienta de recuperación a partir del retriever de ChromaDB
    retriever_tool = create_retriever_tool(
        retriever=retriever,
        name="buscar_en_base_de_conocimiento",
        description=(
            "Busca información relevante en la base de conocimiento vectorial. "
            "Úsala para responder preguntas basándote únicamente en los documentos."
        ),
    )

    # Cargar herramientas MCP (Google Calendar) si están configuradas
    mcp_tools = get_mcp_tools()
    all_tools = [retriever_tool] + mcp_tools

    # Construir el agente con la nueva API de LangChain 1.x
    agent = create_agent(
        model=llm,
        tools=all_tools,
        system_prompt=(
            "Eres un asistente experto en la Copa Mundial FIFA 2026. "
            "SIEMPRE usa primero buscar_en_base_de_conocimiento para obtener la información. "
            + (
                "Cuando el usuario pida agregar partidos al calendario, "
                "usa la información que ya recuperaste de la base de conocimiento para rellenar "
                "directamente los campos del evento (título, fecha, hora, ubicación) "
                "sin pedirle más datos al usuario. "
                "Crea los eventos uno por uno con crear_evento_calendario."
                if mcp_tools else ""
            )
        ),
    )

    return agent


def invoke_agent(agent, question: str) -> str:
    """Invoca el agente y retorna la respuesta como string plano."""
    result = agent.invoke({"messages": [HumanMessage(content=question)]})
    messages = result.get("messages", [])
    if not messages:
        return ""

    content = messages[-1].content

    # Gemini 2.5 Flash puede devolver una lista de bloques de contenido
    if isinstance(content, list):
        partes = [
            bloque.get("text", "") if isinstance(bloque, dict) else str(bloque)
            for bloque in content
            if not isinstance(bloque, dict) or bloque.get("type") == "text"
        ]
        return "".join(partes).strip()

    return str(content).strip()
