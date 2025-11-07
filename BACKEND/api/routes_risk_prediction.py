# api/routes_risk_prediction.py
import pandas as pd
import io
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from typing import List, Dict, Any

# Importar nuestros módulos y modelos Pydantic
from src.ml_processor import (
    AccidentInput, 
    BatchInput,
    load_models,
    preprocess_data,
    get_prediction,
    models_loaded,
    metrics
)

router = APIRouter(
    prefix="/api/risk",
    tags=["Risk Prediction (ML Model)"],
    # Aquí podrías añadir dependencias de seguridad si tuvieras una API key
)

# --- Evento de Inicio ---
@router.on_event("startup")
async def startup_event():
    """Al iniciar la API, carga los modelos en memoria."""
    load_models(model_path="models/")
    print(load_models)


# --- Endpoint 1: Estado del Modelo ---
@router.get("/status")
async def get_model_status():
    """Devuelve el estado de los modelos cargados y sus métricas."""
    if not models_loaded or "Error" in models_loaded:
        raise HTTPException(status_code=503, detail="Modelos no disponibles")
        
    return {
        "status": "operational",
        "models_loaded": models_loaded,
        "metrics": metrics
    }

# --- Endpoint 2: Predicción Individual ---
@router.post("/predict", response_model=Dict[str, Any])
async def predict_single(data: AccidentInput):
    """Predice el riesgo para un único accidente."""
    try:
        # 1. Convertir Pydantic a DataFrame
        input_df = pd.DataFrame([data.model_dump()])
        print("INPUT:", input_df)
        
        # 2. Preprocesar
        processed_df = preprocess_data(input_df)
        print("PROCESSED:", processed_df)
        
        # 3. Predecir
        score = get_prediction(processed_df)[0]
        print(f"Predicted score: {score}")
        
        # 4. Formatear respuesta (cumpliendo con la Hackathon)
        risk_level = "ALTO" if score > 0.5 else ("MEDIO" if score > 0.25 else "BAJO")
        
        return {
            "risk_score": score,
            "risk_level": risk_level,
            "drivers": [  # Drivers simplificados (como pide el desafío)
                f"Comuna: {data.comuna}",
                f"Tipo de Accidente: {data.tipo_accidente}",
                f"Periodo: {data.fecha}"
            ],
            "timestamp": pd.Timestamp.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error en la predicción: {e}")

# --- Endpoint 3: Predicción en Batch ---
@router.post("/predict/batch", response_model=List[Dict[str, Any]])
async def predict_batch(data: BatchInput):
    """Predice el riesgo para una lista (batch) de accidentes."""
    try:
        # 1. Convertir Pydantic a DataFrame
        input_list = [item.model_dump() for item in data.accidents]
        input_df = pd.DataFrame(input_list)
        
        # 2. Preprocesar
        processed_df = preprocess_data(input_df)
        
        # 3. Predecir
        scores = get_prediction(processed_df)
        
        # 4. Formatear respuesta
        results = []
        for i, score in enumerate(scores):
            risk_level = "ALTO" if score > 0.5 else ("MEDIO" if score > 0.25 else "BAJO")
            results.append({
                "risk_score": score,
                "risk_level": risk_level,
                "input_data": input_list[i]
            })
        return results
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error en la predicción batch: {e}")

# --- Endpoint 4: Predicción desde CSV ---
@router.post("/predict/csv")
async def predict_csv(file: UploadFile = File(...)):
    """Predice el riesgo para un CSV completo."""
    if file.content_type != "text/csv":
        raise HTTPException(status_code=400, detail="Tipo de archivo inválido. Se espera text/csv")
        
    try:
        # 1. Leer CSV
        contents = await file.read()
        buffer = io.StringIO(contents.decode('utf-8'))
        input_df = pd.read_csv(buffer)
        
        # Validar columnas mínimas (ajusta según necesidad)
        if not {"comuna", "tipo_accidente", "fecha"}.issubset(input_df.columns):
            raise ValueError("El CSV debe contener las columnas 'comuna', 'tipo_accidente' y 'fecha'")
        
        # 2. Preprocesar
        processed_df = preprocess_data(input_df.copy())
        
        # 3. Predecir
        scores = get_prediction(processed_df)
        
        # 4. Devolver resultados
        input_df["risk_score"] = scores
        return input_df.to_dict(orient="records")

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error procesando el CSV: {e}")

# --- Endpoint 5: Ranking de Comunas ---
@router.get("/comunas/ranking")
async def get_comuna_ranking(limit: int = 5):
    """
    Devuelve un ranking de comunas basado en el AUROC de fairness
    (Datos tomados de tu reporte_metricas.pdf).
    """
    # (Datos estimados de tu gráfico en reporte_metricas.pdf, página 4)
    fairness_data = [
        {"comuna": "CURACAVI", "auroc": 0.99}, 
        {"comuna": "TILTIL", "auroc": 0.98},
        {"comuna": "PIRQUE", "auroc": 0.98},
        {"comuna": "ISLA DE MAIPO", "auroc": 0.97},
        {"comuna": "LO ESPEJO", "auroc": 0.97},
        {"comuna": "SAN JOSE DE MAIPO", "auroc": 0.96},
        {"comuna": "TALAGANTE", "auroc": 0.95},
    ]
    
    return fairness_data[:limit]