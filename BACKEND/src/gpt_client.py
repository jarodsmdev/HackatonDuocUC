import os
from dotenv import load_dotenv
from openai import OpenAI
from openai import AuthenticationError, APIConnectionError, RateLimitError, BadRequestError
# Importar la base de datos
from .database import db_connection, init_db


# Carga variables desde .env (por defecto busca en el directorio actual)
load_dotenv()

# Obtén variables (recomendado: usar os.getenv para valores opcionales)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_SYSTEM_PROMPT = os.getenv("OPENAI_SYSTEM_PROMPT")

print(f"DEBUG: OPENAI_SYSTEM_PROMPT={OPENAI_SYSTEM_PROMPT}")

if not OPENAI_API_KEY:
    raise RuntimeError("Falta OPENAI_API_KEY en las variables de entorno")

if not OPENAI_SYSTEM_PROMPT:
    raise RuntimeError("Falta OPENAI_SYSTEM_PROMPT en las variables de entorno")

# Crea el cliente con tu API key
client = OpenAI(api_key=OPENAI_API_KEY)

def ask_openai(prompt: str, model="gpt-3.5-turbo-0125", temperature=0.7) -> str:
    """
    Envía un prompt a OpenAI y devuelve la respuesta del modelo.
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": OPENAI_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_completion_tokens=500 # Esto limita la cantidad de texto generado, sin afectar el prompt.
        )

        result = response.choices[0].message.content.strip()
        usage = response.usage  # contiene detalles de tokens

        # Guardar en la base de datos
        with db_connection() as conn:
            cursor = conn.execute('''
                INSERT INTO accident_analysis 
                (user_prompt, openai_response, tokens_used, model_used)
                VALUES (?, ?, ?, ?)
            ''', (prompt, result, usage.total_tokens, model))
            analysis_id = cursor.lastrowid
        
        return {
                "message": result,
                "tokens": {
                    "prompt": usage.prompt_tokens,
                    "completion": usage.completion_tokens,
                    "total": usage.total_tokens,
                }
        }
    
    # Manejo de errores específicos
    except AuthenticationError:
        return (
            "Error de autenticación con OpenAI.\n"
            "Verifica que tu API key sea válida y esté configurada correctamente en el archivo .env o el entorno.\n"
            "Puedes generar una nueva aquí: https://platform.openai.com/account/api-keys.\n"
            "Puedes visitar la documentación en Github: https://github.com/jarodsmdev/HackatonDuocUC para más detalles."
        )

    except RateLimitError:
        return "Límite de peticiones alcanzado. Intenta de nuevo en unos segundos."

    except APIConnectionError:
        return "No se pudo conectar con los servidores de OpenAI. Revisa tu conexión a Internet."

    except BadRequestError as e:
        return f"Error en la solicitud: {e}"

    except Exception as e:
        return f"Error inesperado: {type(e).__name__} - {e}"
    
def get_analysis_history(limit: int = 10):
    """Obtiene el historial de análisis"""
    with db_connection() as conn:
        cursor = conn.execute('''
            SELECT id, user_prompt, openai_response, tokens_used, model_used, created_at
            FROM accident_analysis 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,))
        return cursor.fetchall()

def get_analysis_by_id(analysis_id: int):
    """Obtiene un análisis específico por ID"""
    with db_connection() as conn:
        cursor = conn.execute('''
            SELECT * FROM accident_analysis WHERE id = ?
        ''', (analysis_id,))
        return cursor.fetchone()