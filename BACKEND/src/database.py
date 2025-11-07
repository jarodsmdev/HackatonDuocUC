import sqlite3
import os
from contextlib import contextmanager

# Ruta de la base de datos - la guardamos en el directorio raíz
DB_PATH = "smartcities.db"

def get_db_connection():
    """Obtiene una conexión a la base de datos SQLite"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Para acceder a las columnas por nombre
    return conn

def init_db():
    """Inicializa la base de datos con las tablas necesarias"""
    conn = get_db_connection()
    try:
        # Tabla para almacenar las consultas de análisis
        conn.execute('''
            CREATE TABLE IF NOT EXISTS accident_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_prompt TEXT NOT NULL,
                openai_response TEXT NOT NULL,
                tokens_used INTEGER,
                model_used TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        print("Base de datos SQLite inicializada correctamente")
    except Exception as e:
        print(f"Error inicializando la base de datos: {e}")
    finally:
        conn.close()

@contextmanager
def db_connection():
    """Context manager para manejar conexiones a la base de datos"""
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()