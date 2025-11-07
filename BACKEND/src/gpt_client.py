# src/gpt_client.py
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from openai import OpenAI
from openai import AuthenticationError, APIConnectionError, RateLimitError, BadRequestError

# Base de datos local
from .database import db_connection, init_db


# -------------------------------------------------------------------
# Carga robusta del archivo .env
# - Primero intenta cargar el .env ubicado en BACKEND/.env
# - Luego hace un load_dotenv() normal como respaldo
# -------------------------------------------------------------------
ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=ENV_PATH)
load_dotenv()  # fallback por si ejecutan desde otro cwd

# -------------------------------------------------------------------
# Variables de entorno requeridas
# -------------------------------------------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_SYSTEM_PROMPT = os.getenv("OPENAI_SYSTEM_PROMPT")
# Permite configurar el modelo por entorno. Valor seguro por defecto si no se define.
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

if not OPENAI_API_KEY:
    raise RuntimeError("Falta OPENAI_API_KEY en las variables de entorno")

if not OPENAI_SYSTEM_PROMPT:
    raise RuntimeError("Falta OPENAI_SYSTEM_PROMPT en las variables de entorno")

# -------------------------------------------------------------------
# Cliente de OpenAI
# -------------------------------------------------------------------
client = OpenAI(api_key=OPENAI_API_KEY)


def ask_openai(
    prompt: str,
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_completion_tokens: int = 500,
) -> Dict[str, Any]:
    """
    Envía un prompt a OpenAI y devuelve la respuesta del modelo.
    También registra el intercambio en la base de datos local.

    Devuelve:
        {
            "message": "<texto respuesta>",
            "tokens": {"prompt": int, "completion": int, "total": int},
            "model": "<modelo_usado>"
        }
    """
    selected_model = model or OPENAI_MODEL

    try:
        # Chat Completions (API clásica)
        response = client.chat.completions.create(
            model=selected_model,
            messages=[
                {"role": "system", "content": OPENAI_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
            max_completion_tokens=max_completion_tokens,
        )

        # Extraer contenido y uso
        result = (response.choices[0].message.content or "").strip()
        usage = response.usage  # prompt_tokens, completion_tokens, total_tokens

        # Asegurar que la base esté inicializada
        try:
            init_db()
        except Exception:
            # Si ya está inicializada, ignoramos
            pass

        # Guardar en la base de datos
        with db_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO accident_analysis
                (user_prompt, openai_response, tokens_used, model_used)
                VALUES (?, ?, ?, ?)
                """,
                (prompt, result, getattr(usage, "total_tokens", None), selected_model),
            )
            _ = cursor.lastrowid  # Si se quiere retornar más adelante

        return {
            "message": result,
            "tokens": {
                "prompt": getattr(usage, "prompt_tokens", None),
                "completion": getattr(usage, "completion_tokens", None),
                "total": getattr(usage, "total_tokens", None),
            },
            "model": selected_model,
        }

    # Manejo de errores específicos de la librería
    except AuthenticationError:
        return {
            "error": True,
            "message": (
                "Error de autenticación con OpenAI. Verifica que tu API key sea válida "
                "y esté configurada correctamente en el archivo .env o el entorno."
            ),
        }

    except RateLimitError:
        return {"error": True, "message": "Límite de peticiones alcanzado. Intenta de nuevo en unos segundos."}

    except APIConnectionError:
        return {"error": True, "message": "No se pudo conectar con OpenAI. Revisa tu conexión a Internet."}

    except BadRequestError as e:
        return {"error": True, "message": f"Error en la solicitud a OpenAI: {e}"}

    except Exception as e:
        return {"error": True, "message": f"Error inesperado: {type(e).__name__} - {e}"}


def get_analysis_history(limit: int = 10):
    """
    Obtiene el historial de análisis más recientes.
    """
    with db_connection() as conn:
        cursor = conn.execute(
            """
            SELECT id, user_prompt, openai_response, tokens_used, model_used, created_at
            FROM accident_analysis
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        )
        return cursor.fetchall()


def get_analysis_by_id(analysis_id: int):
    """
    Obtiene un análisis específico por ID.
    """
    with db_connection() as conn:
        cursor = conn.execute(
            """
            SELECT id, user_prompt, openai_response, tokens_used, model_used, created_at
            FROM accident_analysis
            WHERE id = ?
            """,
            (analysis_id,),
        )
        return cursor.fetchone()


if __name__ == "__main__":
    # Pequeña prueba manual (no envía la API key a stdout)
    print("✅ gpt_client listo. Modelo por defecto:", OPENAI_MODEL)
