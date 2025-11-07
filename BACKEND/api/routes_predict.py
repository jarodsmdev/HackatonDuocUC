from fastapi import APIRouter
from pydantic import BaseModel
from src.gpt_client import ask_openai

router = APIRouter()

class PredictRequest(BaseModel):
    prompt: str

@router.post("/predict")
async def predict(request: PredictRequest) -> dict:
    """
    Devuelve {"score": float, "drivers": [top_features]} o una respuesta del modelo.
    """
    response = ask_openai(request.prompt)
    return {"score": 0.85, "drivers": [response]}
