import sys
import os

# FIX: Agregar carpeta raiz al PYTHONPATH
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from src.config import FAISS_INDEX_PATH, GOOGLE_API_KEY


class RAGEngine:
    def __init__(self):
        # Embeddings locales (MiniLM)
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # LLM Gemini (solo para generar respuestas)
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-3.5-flash",
            google_api_key=GOOGLE_API_KEY,
            temperature=0.3
        )
        
        self.vectorstore = None
        self.retriever = None
        self.chat_history = []
        self._load_vectorstore()
    
    def _load_vectorstore(self):
        if os.path.exists(FAISS_INDEX_PATH):
            self.vectorstore = FAISS.load_local(
                FAISS_INDEX_PATH, 
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            self.retriever = self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 5}
            )
            print("Indice FAISS cargado correctamente.")
        else:
            print("No se encontro el indice FAISS. Ejecuta ingest.py primero.")
    
    def _format_docs(self, docs):
        return "\n\n".join(doc.page_content for doc in docs)
    
    def _get_sources(self, docs):
        return list(set([
            os.path.basename(doc.metadata.get("source", "Desconocido")) 
            for doc in docs
        ]))
    
    def query(self, question: str, section_filter: str = None):
        if not self.retriever:
            return {
                "answer": "El motor RAG no esta inicializado. Ejecuta primero el pipeline de ingesta.",
                "sources": []
            }
        
        # Enriquecer pregunta si hay filtro de seccion
        if section_filter:
            question = f"Responde basandote en la seccion '{section_filter}' del documento. Pregunta: {question}"
        
        # Recuperar documentos relevantes
        retrieved_docs = self.retriever.invoke(question)
        context = self._format_docs(retrieved_docs)
        sources = self._get_sources(retrieved_docs)
        
        # Construir prompt con historial conversacional
        prompt = ChatPromptTemplate.from_messages([
            ("system", (
                "Eres un asistente inteligente especializado en responder preguntas "
                "basandote EXCLUSIVAMENTE en el contexto proporcionado a continuacion.\n\n"
                "REGLAS:\n"
                "- Si la respuesta no esta en el contexto, di claramente que no tienes suficiente informacion.\n"
                "- No inventes informacion que no aparezca en el contexto.\n"
                "- Usa formato Markdown para mejor legibilidad (negritas, listas, etc.).\n\n"
                "CONTEXTO:\n{context}"
            )),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}")
        ])
        
        # Crear cadena: prompt -> llm -> parser
        chain = prompt | self.llm | StrOutputParser()
        
        # Invocar
        answer = chain.invoke({
            "context": context,
            "question": question,
            "chat_history": self.chat_history
        })
        
        # Actualizar historial (limitado a ultimos 6 intercambios = 12 mensajes)
        self.chat_history.extend([
            HumanMessage(content=question),
            AIMessage(content=answer)
        ])
        if len(self.chat_history) > 12:
            self.chat_history = self.chat_history[-12:]
        
        return {"answer": answer, "sources": sources}
    
    def clear_memory(self):
        self.chat_history = []