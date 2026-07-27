# 🤖 Chatbot RAG con Gemini y PDFs

## Descripción del Proyecto

Este proyecto es un **Chatbot de Inteligencia Artificial** basado en la arquitectura **RAG (Retrieval-Augmented Generation)** que permite realizar consultas inteligentes sobre un conjunto de documentos PDF. El sistema extrae el contenido de los PDFs, lo divide en chunks, genera embeddings usando el modelo de Google Gemini, y responde preguntas basándose únicamente en la información contenida en los documentos.

## Arquitectura de la Solución

La solución se divide en dos componentes principales:

### 1. Pipeline de Ingesta (`src/ingest.py`)
- **Carga**: Utiliza `PyPDFDirectoryLoader` para leer todos los PDFs de la carpeta `docs/`.
- **Chunking**: Aplica `RecursiveCharacterTextSplitter` para dividir el texto en fragmentos manejables.
- **Embeddings**: Genera vectores semánticos con `GoogleGenerativeAIEmbeddings` (modelo `embedding-001`).
- **Vector Store**: Almacena los embeddings en **FAISS** para búsqueda eficiente por similitud.
- **Metadatos**: Guarda información de documentos y secciones en **MySQL**.

### 2. Motor de Recuperación y Generación (`src/rag_engine.py` + `src/app.py`)
- **Recuperación**: Busca los chunks más relevantes usando similitud de coseno sobre el índice FAISS.
- **Generación**: Envía el contexto recuperado al modelo **Gemini 1.5 Flash** para generar respuestas coherentes.
- **Memoria**: Mantiene contexto conversacional con `ConversationBufferMemory`.
- **Interfaz**: Aplicación web interactiva construida con **Streamlit**.

## Tecnologías Utilizadas

| Tecnología | Propósito |
|------------|-----------|
| Python 3.10+ | Lenguaje principal |
| Streamlit | Interfaz web tipo chatbot |
| LangChain | Orquestación del pipeline RAG |
| Google Generative AI | Embeddings y LLM (Gemini) |
| FAISS | Base de datos vectorial local |
| MySQL | Metadatos, historial y secciones |
| PyPDFDirectoryLoader | Extracción de texto de PDFs |

## Requisitos y Paquetes Requeridos

- Python 3.10 o superior
- MySQL Server 8.0+
- Cuenta de Google AI Studio (para API Key de Gemini)

Instalación de dependencias:
```bash
pip install -r requirements.txt