import os
from dotenv import load_dotenv

# Buscar el .env en la carpeta raíz del proyecto (un nivel arriba de src/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(BASE_DIR, ".env")

# Cargar explícitamente desde la ruta correcta
load_dotenv(dotenv_path=env_path)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "rag_chatbot"),
    "port": int(os.getenv("DB_PORT", 3306)),
}

DOCS_PATH = os.getenv("DOCS_PATH", "./docs")
FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "./faiss_index")