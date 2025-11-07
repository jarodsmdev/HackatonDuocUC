from http.client import HTTPException
from fastapi import APIRouter
from pydantic import BaseModel
from src.gpt_client import ask_openai
import asyncio

router = APIRouter()

class CoachRequest(BaseModel):
    prompt: str

@router.post("/coach")
async def coach(request: CoachRequest) -> dict:
    """
    Devuelve un plan textual basado en la base de conocimiento /kb.
    """
    try:
        # Ejecuta ask_openai en un hilo separado (no bloquea el event loop)
        plan = await asyncio.to_thread(
            ask_openai, f"Genera un plan de coaching para: {request.prompt}"
        )

        return {"plan": plan}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar plan: {str(e)}")
