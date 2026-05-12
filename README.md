# VectoAgent - Agente ReAct con RAG

Implementacion de un agente ReAct (Reasoning + Acting) con RAG (Retrieval-Augmented Generation)
usando LangChain, Gemini 2.5 Flash y ChromaDB como vector store.

La base de conocimiento se carga desde archivos Markdown en `data/markdown` y se fragmenta
segun la configuracion en `.env`.

---

## Arquitectura

```
Usuario -> Pregunta -> [Embedding] -> ChromaDB -> Contexto
                                                 -> Agente ReAct (Gemini)
                                                 -> Respuesta final
```

---

## Stack tecnologico

| Componente | Tecnologia |
|---|---|
| LLM | Gemini 2.5 Flash (`gemini-2.5-flash`) |
| Embeddings | Google `gemini-embedding-001` |
| Vector Store | ChromaDB (persistencia configurable por `.env`) |
| Framework | LangChain 0.3+ |
| UI Chat | Streamlit |
| Evaluacion | RAGAS |

---

## Instalacion

```bash
cd VectoAgent

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt
```

---

## Configuracion

1. Copia `.env.example` a `.env`
2. Completa `GOOGLE_API_KEY` y `LANGCHAIN_API_KEY`

Variables relevantes:

```env
# Base de conocimiento markdown
KNOWLEDGE_BASE_DIR=data/markdown
KNOWLEDGE_BASE_GLOB=**/*.md

# Chunking
CHUNK_SIZE=700
CHUNK_OVERLAP=120

# Recuperacion
RETRIEVER_K=3

# Persistencia Chroma
CHROMA_PERSIST_DIR=./chroma_db
CHROMA_COLLECTION=vectoagent_docs
CHROMA_RESET_ON_START=false
```

Si `CHROMA_RESET_ON_START=true`, la base vectorial se elimina y reconstruye al iniciar.

---

## Ejecucion

```bash
# CLI
python main.py

# Interfaz grafica tipo chat
streamlit run app.py
```

---

## Estructura del proyecto

```
VectoAgent/
├── app.py                    # Chat UI con Streamlit
├── main.py                   # Ejecucion por consola
├── .env.example
├── requirements.txt
├── data/
│   ├── knowledge_base.py     # Loader markdown + chunking configurable
│   └── markdown/             # Base de conocimiento fuente
├── src/
│   ├── agent.py
│   ├── embeddings.py
│   ├── evaluation.py
│   ├── pipeline.py           # Runtime compartido
│   └── vector_store.py
└── chroma_db/                # Persistencia vectorial
```
