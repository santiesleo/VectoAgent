import os

import streamlit as st
from dotenv import load_dotenv

# Cargar entorno antes de inicializar el runtime.
load_dotenv()

from src.agent import invoke_agent
from src.pipeline import build_runtime, get_retriever_k


st.set_page_config(
    page_title="VectoAgent Chat",
    page_icon="💬",
    layout="wide",
)


@st.cache_resource
def init_runtime():
    return build_runtime()


def init_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "Hola. Soy VectoAgent. Preguntame sobre Bolivar, "
                    "San Martin, Sucre o Santander."
                ),
            }
        ]


def render_sidebar() -> None:
    st.sidebar.title("Configuracion")
    st.sidebar.caption("Valores leidos desde .env")
    st.sidebar.write(f"KNOWLEDGE_BASE_DIR: {os.getenv('KNOWLEDGE_BASE_DIR', 'data/markdown')}")
    st.sidebar.write(f"CHUNK_SIZE: {os.getenv('CHUNK_SIZE', '700')}")
    st.sidebar.write(f"CHUNK_OVERLAP: {os.getenv('CHUNK_OVERLAP', '120')}")
    st.sidebar.write(f"RETRIEVER_K: {get_retriever_k()}")
    st.sidebar.write(f"CHROMA_PERSIST_DIR: {os.getenv('CHROMA_PERSIST_DIR', './chroma_db')}")
    st.sidebar.write(f"CHROMA_COLLECTION: {os.getenv('CHROMA_COLLECTION', 'vectoagent_docs')}")

    if st.sidebar.button("Limpiar chat"):
        st.session_state.messages = st.session_state.messages[:1]
        st.rerun()


def main() -> None:
    st.title("VectoAgent")
    st.caption("Chat RAG sobre independencia latinoamericana")

    init_state()
    render_sidebar()

    try:
        with st.spinner("Inicializando embeddings, Chroma y agente..."):
            agent_executor, retriever = init_runtime()
    except Exception as exc:
        st.error(f"Error al inicializar el runtime: {exc}")
        st.stop()

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_prompt = st.chat_input("Escribe tu pregunta...")
    if not user_prompt:
        return

    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    try:
        with st.spinner("Pensando..."):
            answer = invoke_agent(agent_executor, user_prompt)
            contexts = retriever.invoke(user_prompt)
    except Exception as exc:
        st.error(f"Error durante la consulta: {exc}")
        return

    st.session_state.messages.append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.markdown(answer)
        with st.expander("Ver contexto recuperado"):
            for idx, doc in enumerate(contexts, start=1):
                source = doc.metadata.get("source", "sin_fuente")
                st.markdown(f"**Fragmento {idx}**  ")
                st.markdown(f"Fuente: {source}")
                st.write(doc.page_content)


if __name__ == "__main__":
    main()
