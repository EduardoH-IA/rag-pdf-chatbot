import sys
import os

# FIX CRITICO: Agregar carpeta raiz al PYTHONPATH antes de cualquier import de src
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import streamlit as st
import uuid
from src.rag_engine import RAGEngine
from src.database import (
    init_db, get_documents, get_sections_by_doc,
    save_conversation, get_conversation_history
)
from src.config import GOOGLE_API_KEY

# Configuracion de pagina
st.set_page_config(
    page_title="Chatbot RAG PDF",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializacion de session state
if "engine" not in st.session_state:
    st.session_state.engine = RAGEngine()
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "selected_doc" not in st.session_state:
    st.session_state.selected_doc = None
if "selected_section" not in st.session_state:
    st.session_state.selected_section = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)


def main():
    init_db()
    
    # ================= SIDEBAR =================
    with st.sidebar:
        st.title("Menu de Documentos")
        st.markdown("---")
        
        if not GOOGLE_API_KEY:
            st.error("No se encontro GOOGLE_API_KEY. Configura el archivo .env")
            st.stop()
        
        docs = get_documents()
        if not docs:
            st.warning("No hay documentos indexados. Ejecuta `python src/ingest.py`")
        else:
            st.subheader("Documentos disponibles")
            for doc in docs:
                btn_label = f"{doc['title']}"
                if st.button(btn_label, key=f"doc_{doc['id']}"):
                    st.session_state.selected_doc = doc
                    st.session_state.selected_section = None
                    st.rerun()
        
        st.markdown("---")
        st.subheader("Preguntas de ejemplo")
        if st.button("Cual es el resumen ejecutivo del documento?", key="ej1"):
            handle_query("Cual es el resumen ejecutivo del documento?")
        if st.button("Que conclusiones se presentan en el informe?", key="ej2"):
            handle_query("Que conclusiones se presentan en el informe?")
        
        st.markdown("---")
        if st.button("Limpiar conversacion", key="clear"):
            st.session_state.messages = []
            st.session_state.engine.clear_memory()
            st.rerun()
        
        st.caption("Powered by Gemini + RAG")

    # ================= MAIN CONTENT =================
    st.markdown('<div class="main-header">Asistente Inteligente de Documentos</div>', unsafe_allow_html=True)
    
    if st.session_state.selected_doc:
        doc = st.session_state.selected_doc
        st.info(f"Documento seleccionado: **{doc['title']}**")
        
        sections = get_sections_by_doc(doc["id"])
        if sections:
            st.subheader("Secciones disponibles")
            cols = st.columns(3)
            for i, sec in enumerate(sections):
                with cols[i % 3]:
                    btn_label = sec["section_title"][:50] + "..." if len(sec["section_title"]) > 50 else sec["section_title"]
                    if st.button(btn_label, key=f"sec_{sec['id']}", help=sec["section_title"]):
                        st.session_state.selected_section = sec["section_title"]
                        query = f"Explica el contenido de la seccion: {sec['section_title']}"
                        handle_query(query, section=sec["section_title"])
        else:
            st.info("No se detectaron secciones en este documento.")
    else:
        st.info("Selecciona un documento del menu lateral para comenzar.")
    
    st.markdown("---")
    
    # ================= CHAT AREA =================
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
    
    # Input de usuario
    user_input = st.chat_input("Escribe tu consulta aqui...")
    if user_input:
        section = st.session_state.selected_section if st.session_state.selected_section else None
        handle_query(user_input, section=section)


def handle_query(question, section=None):
    st.session_state.messages.append({"role": "user", "content": question})
    save_conversation(st.session_state.session_id, "user", question)
    
    with st.spinner("Buscando en los documentos..."):
        result = st.session_state.engine.query(question, section_filter=section)
    
    answer = result["answer"]
    sources = result.get("sources", [])
    
    sources_text = "\n\n**Fuentes consultadas:** " + ", ".join(sources) if sources else ""
    full_response = f"{answer}{sources_text}"
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    save_conversation(st.session_state.session_id, "assistant", full_response)
    
    st.rerun()


if __name__ == "__main__":
    main()