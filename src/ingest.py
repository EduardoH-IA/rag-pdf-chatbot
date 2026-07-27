import sys
import os
import time

# FIX: Agregar carpeta raiz al PYTHONPATH
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from src.config import DOCS_PATH, FAISS_INDEX_PATH
from src.database import init_db, insert_document, insert_section
from collections import defaultdict


def extract_toc_heuristic(text, pages):
    lines = text.split('\n')
    sections = []
    current_title = None
    current_start = 0
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        if (stripped.isupper() and len(stripped) > 3 and len(stripped) < 100) or \
           (stripped and stripped[0].isdigit() and '.' in stripped[:5] and len(stripped) < 100):
            if current_title:
                sections.append({"title": current_title, "start": current_start, "end": i})
            current_title = stripped
            current_start = i
    
    if current_title:
        sections.append({"title": current_title, "start": current_start, "end": len(lines)})
    
    return sections


def ingest_documents():
    init_db()
    print("Cargando PDFs desde:", DOCS_PATH)
    loader = PyPDFDirectoryLoader(DOCS_PATH)
    documents = loader.load()
    
    if not documents:
        print("No se encontraron PDFs en la carpeta docs/")
        return
    
    print(f"{len(documents)} paginas cargadas")
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    
    chunks = text_splitter.split_documents(documents)
    print(f"{len(chunks)} chunks generados")
    
    # EMBEDDINGS LOCALES con MiniLM
    print("Descargando modelo all-MiniLM-L6-v2 (solo la primera vez)...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    
    print("Generando embeddings...")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    
    os.makedirs(FAISS_INDEX_PATH, exist_ok=True)
    vectorstore.save_local(FAISS_INDEX_PATH)
    
    docs_by_file = defaultdict(list)
    for doc in documents:
        docs_by_file[doc.metadata["source"]].append(doc)
    
    for filepath, pages in docs_by_file.items():
        filename = os.path.basename(filepath)
        full_text = "\n".join([p.page_content for p in pages])
        
        doc_id = insert_document(
            filename=filename,
            title=filename.replace(".pdf", ""),
            total_pages=len(pages)
        )
        
        sections = extract_toc_heuristic(full_text, pages)
        for sec in sections[:20]:
            insert_section(doc_id, sec["title"], sec["start"], sec["end"])
    
    print("Ingesta completada. Indice FAISS y MySQL actualizados.")


if __name__ == "__main__":
    ingest_documents()