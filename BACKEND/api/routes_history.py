from fastapi import APIRouter, HTTPException
from src.gpt_client import get_analysis_history, get_analysis_by_id

router = APIRouter()

@router.get("/history")
async def get_history(limit: int = 10):
    """Obtiene el historial de análisis recientes"""
    try:
        analyses = get_analysis_history(limit)
        return [
            {
                "id": analysis["id"],
                "user_prompt": analysis["user_prompt"][:100] + "..." if len(analysis["user_prompt"]) > 100 else analysis["user_prompt"],
                "tokens_used": analysis["tokens_used"],
                "model_used": analysis["model_used"],
                "created_at": analysis["created_at"]
            }
            for analysis in analyses
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo historial: {str(e)}")

@router.get("/analysis/{analysis_id}")
async def get_analysis(analysis_id: int):
    """Obtiene un análisis específico por ID"""
    try:
        analysis = get_analysis_by_id(analysis_id)
        if not analysis:
            raise HTTPException(status_code=404, detail="Análisis no encontrado")
        return dict(analysis)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo análisis: {str(e)}")

@router.get("/stats")
async def get_stats():
    """Obtiene estadísticas básicas del sistema"""
    try:
        analyses = get_analysis_history(1000)  # Obtener muchos para estadísticas
        total_analyses = len(analyses)
        total_tokens = sum(analysis["tokens_used"] or 0 for analysis in analyses)
        
        return {
            "total_analyses": total_analyses,
            "total_tokens_used": total_tokens,
            "average_tokens_per_analysis": total_tokens / total_analyses if total_analyses > 0 else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo estadísticas: {str(e)}")