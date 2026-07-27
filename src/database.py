import mysql.connector
from mysql.connector import Error
from src.config import DB_CONFIG

def get_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Error conectando a MySQL: {e}")
        raise

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INT AUTO_INCREMENT PRIMARY KEY,
            filename VARCHAR(255) NOT NULL,
            title VARCHAR(255),
            total_pages INT,
            indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS document_sections (
            id INT AUTO_INCREMENT PRIMARY KEY,
            doc_id INT,
            section_title VARCHAR(500),
            page_start INT,
            page_end INT,
            FOREIGN KEY (doc_id) REFERENCES documents(id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            session_id VARCHAR(100),
            role ENUM('user', 'assistant'),
            message TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    cursor.close()
    conn.close()

def save_conversation(session_id, role, message):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO conversations (session_id, role, message) VALUES (%s, %s, %s)",
        (session_id, role, message)
    )
    conn.commit()
    cursor.close()
    conn.close()

def get_conversation_history(session_id, limit=10):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT role, message FROM conversations WHERE session_id = %s ORDER BY timestamp DESC LIMIT %s",
        (session_id, limit)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows[::-1]

def get_documents():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM documents")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def get_sections_by_doc(doc_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM document_sections WHERE doc_id = %s", (doc_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def insert_document(filename, title, total_pages):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO documents (filename, title, total_pages) VALUES (%s, %s, %s)",
        (filename, title, total_pages)
    )
    doc_id = cursor.lastrowid
    conn.commit()
    cursor.close()
    conn.close()
    return doc_id

def insert_section(doc_id, section_title, page_start, page_end):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO document_sections (doc_id, section_title, page_start, page_end) VALUES (%s, %s, %s, %s)",
        (doc_id, section_title, page_start, page_end)
    )
    conn.commit()
    cursor.close()
    conn.close()