# 🤖 Chatbot RAG con Gemini y PDFs

## Descripción del Proyecto

Este proyecto es un **Chatbot de Inteligencia Artificial** basado en la arquitectura **RAG (Retrieval-Augmented Generation)** que permite realizar consultas inteligentes sobre un conjunto de documentos PDF. El sistema extrae el contenido de los PDFs, lo divide en chunks, genera embeddings usando el modelo de Google Gemini, y responde preguntas basándose únicamente en la información contenida en los documentos.

## Caso de Uso: E-Commerce BimBam Buy

Se tomo como ejemplo el Caso de uso relacionados con la tienda Online/E-Commerce BimBam Buy, en donde el agente realiza una consulta a los documentos PDF para obtener información sobre los productos, envios, devoluciones, etc. 

BimBam Buy es un E-commerce multiplataforma enfocado en la experiencia de compra digital ágil y segura. Se destaca por un modelo de negocio orientado al cliente, con políticas robustas de reembolso, un programa de afiliados dinámico y una infraestructura logística optimizada para garantizar entregas rápidas y soporte constante al usuário final.

La documentación de BimBam Buy disponible para el agente es la siguiente:

- Política de Reembolsos y Devoluciones de BimBam Buy.pdf
- Programa de Afiliados de BimBam Buy.pdf
- Guía de Tiempos y Costos de Envío de BimBam Buy.pdf
- Preguntas_Frecuentes_sobre_Métodos_de_Pago_de_BimBam_Buy.pdf
- Manual de Garantía de Productos de BimBam Buy.pdf

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

## Arquitectura inicaal para el despliegue en Oracle Cloud Infraestrcture (OCI)

![Arquitectura RAG Chatbot IA](/imgs/arquitectura_oci_rag_chatbot.png)  

## Tecnologías Utilizadas

| Tecnología | Propósito |
|------------|-----------|
| Python 3.10+ | Lenguaje principal |
| Streamlit | Interfaz web tipo chatbot |
| LangChain | Orquestación del pipeline RAG |
| Google Generative AI | Embeddings y LLM (Gemini) |
| FAISS | Base de datos vectorial local |
| MariaDB | Metadatos, historial y secciones |
| PyPDFDirectoryLoader | Extracción de texto de PDFs |


## Estructura de Proyecto

rag-pdf-chatbot/
├── .env.example            # Archivo de variables de entorno de ejemplo  
├── .gitignore              # Archivo de ignore
├── README.md               # Archivo de documentación
├── Instalación.md          # Archivo de instalación
├── requirements.txt        # Archivo de dependencias
├── docs/                   # PDFs BimBam Buy a consultar
├── imgs/                     # Iconos e imágenes de la UI
├── sql/
│   └── schema.sql            # Script MariaDB/MySQL
└── src/
    ├── __init__.py
    ├── config.py             # Variables de entorno
    ├── database.py           # Conexión y modelos MariaDB/MySQL
    ├── ingest.py             # Pipeline de Ingesta
    ├── rag_engine.py         # Motor RAG + Gemini
    └── app.py                # Interfaz Web utilizando Streamlit

## Requisitos y Paquetes Requeridos

- Python 3.10 o superior
- PIP 
- FAISS (base de datos vectorial local)
- MariaDB/MySQL Server 8.0+
- all-MiniLM-L6-v2 Procesamiento de Lenguaje Natural (NLP) (embeddings locales)
- Cuenta de Google AI Studio (para API Key de Gemini) (recuperación)
- Gemini-3.5-flash (LLM) 

# Paquetes Requeridos

- langchain-community==0.2.15
- langchain-google-genai==1.0.10
- langchain-text-splitters==0.2.4
- langchain-huggingface==0.0.3
- PyPDF2==3.0.1
- faiss-cpu==1.14.3
- sentence-transformers==3.0.1
- python-dotenv==1.0.1
- mysql-connector-python==9.0.0
- google-generativeai==0.7.2

# Base de datos

# Estructura y Modelo de Entidad Relación (MER)

La base de datos rag_chatbot contiene las siguientes tablas:

| Tabla               | Descripción                                             |
| ------------------- | ------------------------------------------------------- |
| `documents`         | Almacena metadatos de cada PDF indexado                 |
| `document_sections` | Guarda las secciones/temas detectados en cada documento |
| `conversations`     | Historial completo de conversaciones del chatbot        |

# Diagrama Relacional (Modelo Entidad Relación)

documents (1) ───────< (N) document_sections
    │
    └── No relación directa con conversations (independiente)

# Diccionario de Datos

## Campos por Tabla

### documents (tabla)
-   id (PK, INT, AUTO_INCREMENT)
-   filename (VARCHAR 255)
-   title (VARCHAR 255)
-   total_pages (INT)
-   indexed_at (TIMESTAMP)

### document_sections (tabla)
-   id (PK, INT, AUTO_INCREMENT)
-   doc_id (FK, INT)
-   section_title (VARCHAR 500)
-   page_start (INT)
-   page_end (INT)

### conversations (tabla)
-   id (PK, INT, AUTO_INCREMENT)
-   session_id (VARCHAR 100)
-   role (ENUM: 'user', 'assistant')
-   message (TEXT)
-   timestamp (TIMESTAMP)

## Instalación y ejecución

# Preparar de la Base de Datos
```bash
mysql -u root -p < sql/schema.sql
```
# Crear entorno virtual
    ```bash
python -m venv venv
```

# Activar entorno virtual
```bash
source venv/bin/activate
```
# Configurar variables de entorno
```bash
cp .env.example .env
``` 
Edita el archivo .env con tus credenciales:

- GOOGLE_API_KEY: Obténla desde Google AI Studio
- DB_PASSWORD: Contraseña de tu usuario MySQL

# Instalar de dependencias:
```bash 
pip install -r requirements.txt
```
# Preparar PDF
Copiar archivos PDF a la carpeta docs/

# Ejecutar el pipeline de Ingesta de PDF
```bash
python src/ingest.py
```

# Ejecutar el Chatbot
```bash
streamlit run streamlit_app.py
```
La aplicación estará disponible en http://localhost:8501.

## ¿Cómo funciona?

Se trata de una pantalla dividida en dos partes, la barra lateral izquierda y el contenido principal.

### Barra lateral izquierda

En la barra lateral izquierda se encuentra el menú de documentos, donde se pueden ver los documentos que se han indexado en la base de datos.

### Contenido principal

En el contenido principal se encuentra el chatbot, donde se pueden visualizar un conjunto de botones asociados a cada sección de los documentos a consulta o simplemente se puede hacer preguntas en el espacio chatbot para obtener información sobre los documentos que se han indexado en la base de datos.

![Home Chatbot IA + RAG](/imgs/rag_chatbot-IA_IMG_Home.png)  
