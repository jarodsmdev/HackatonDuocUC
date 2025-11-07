# api/routes_risk_prediction.py
from __future__ import annotations

import io
import json
import unicodedata
from pathlib import Path
from typing import List, Dict, Any

import joblib
import pandas as pd
from fastapi import APIRouter, HTTPException, UploadFile, File

# Importar nuestros módulos y modelos Pydantic
from src.ml_processor import (
    AccidentInput,
    BatchInput,
    load_models,
    preprocess_data,
    get_prediction,
    models_loaded,
    metrics,
)

router = APIRouter(
    prefix="/api/risk",
    tags=["Risk Prediction (ML Model)"],
)

# =========================
# Utilidades de normalización
# =========================

def _strip_accents(s: str | None) -> str | None:
    if s is None:
        return s
    return "".join(
        c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn"
    )

def _norm_region(x: str | None) -> str | None:
    """
    Normaliza la región a la forma usada en el entrenamiento.
    Ajusta la devolución a "METROPOLITANA" o "RM" según tu dataset.
    """
    if not x:
        return x
    v = _strip_accents(x).upper().strip()
    if v in {"RM", "REGION METROPOLITANA", "METROPOLITANA"}:
        return "METROPOLITANA"  # cambia a "RM" si así quedó en tu entrenamiento
    return v

def _norm_accident_label(x: str | None) -> str | None:
    """
    Crea la etiqueta que el modelo espera (columna 'Claseaccid'):
    - sin acentos
    - capitalización tipo Título
    - mapeo de sinónimos comunes
    """
    if not x:
        return x
    v = _strip_accents(x).lower().strip()
    mapping = {
        "colision": "Colision",
        "choque": "Colision",
        "atropello": "Atropello",
        "volcamiento": "Volcamiento",
        "incendio": "Incendio",
        "despiste": "Despiste",
        # agrega aquí otras clases reales de tu dataset si las tuvieras
    }
    return mapping.get(v, v.title())

def _harmonize_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ajusta columnas del request a lo que espera el modelo:
    - comuna -> upper
    - region -> normaliza ('METROPOLITANA'/'RM')
    - tipo_accidente -> Claseaccid (sin acentos, título)
    - fecha -> Fecha (si tu pipeline lo requiere así)
    """
    df = df.copy()

    if "comuna" in df.columns:
        df["comuna"] = df["comuna"].astype(str).str.upper().str.strip()

    if "region" in df.columns:
        df["region"] = df["region"].apply(_norm_region)

    if "tipo_accidente" in df.columns and "Claseaccid" not in df.columns:
        df["Claseaccid"] = df["tipo_accidente"].apply(_norm_accident_label)

    if "fecha" in df.columns and "Fecha" not in df.columns:
        df["Fecha"] = df["fecha"]

    return df

def _align_to_expected_columns(X: pd.DataFrame) -> pd.DataFrame:
    """
    Si guardaste columnas esperadas en model_artifacts.joblib (clave 'feature_columns'),
    reindexa para que el orden/coincidencia sea exacto. Si no existe, deja X tal cual.
    """
    try:
        artifacts_path = Path("models") / "model_artifacts.joblib"
        if artifacts_path.exists():
            artifacts = joblib.load(artifacts_path)
            expected = artifacts.get("feature_columns")
            if expected:
                return X.reindex(columns=expected, fill_value=0)
    except Exception:
        # No impedir la predicción por un reindex fallido
        pass
    return X


# =========================
# Eventos
# =========================

@router.on_event("startup")
async def startup_event():
    """Al iniciar la API, carga los modelos en memoria."""
    load_models(model_path="models/")
    print(load_models)


# =========================
# Endpoints
# =========================

# Estado del modelo
@router.get("/status")
async def get_model_status():
    """Devuelve el estado de los modelos cargados y sus métricas."""
    if not models_loaded or "Error" in models_loaded:
        raise HTTPException(status_code=503, detail="Modelos no disponibles")
    return {
        "status": "operational",
        "models_loaded": models_loaded,
        "metrics": metrics,
    }


# Predicción individual
@router.post("/predict", response_model=Dict[str, Any])
async def predict_single(data: AccidentInput):
    """Predice el riesgo para un único accidente."""
    try:
        # 1) Pydantic → DataFrame
        input_df = pd.DataFrame([data.model_dump()])

        # 1.5) Armonización (crea 'Claseaccid', normaliza comuna/region/fecha)
        input_df = _harmonize_df(input_df)

        # 2) Preprocesar
        processed_df = preprocess_data(input_df)

        # 2.5) Alinear columnas a las del entrenamiento (si existe feature_columns)
        processed_df = _align_to_expected_columns(processed_df)

        # 3) Predecir
        score = float(get_prediction(processed_df)[0])

        # 4) Formatear respuesta
        risk_level = "ALTO" if score > 0.5 else ("MEDIO" if score > 0.25 else "BAJO")

        return {
            "risk_score": score,
            "risk_level": risk_level,
            "drivers": [
                f"Comuna: {data.comuna}",
                f"Tipo de Accidente: {data.tipo_accidente}",
                f"Periodo: {data.fecha}",
            ],
            "timestamp": pd.Timestamp.now().isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error en la predicción: {e}")


# Predicción en batch
@router.post("/predict/batch", response_model=List[Dict[str, Any]])
async def predict_batch(data: BatchInput):
    """Predice el riesgo para una lista (batch) de accidentes."""
    try:
        # 1) Pydantic → DataFrame
        input_list = [item.model_dump() for item in data.accidents]
        input_df = pd.DataFrame(input_list)

        # 1.5) Armonización
        input_df = _harmonize_df(input_df)

        # 2) Preprocesar
        processed_df = preprocess_data(input_df)

        # 2.5) Alinear columnas
        processed_df = _align_to_expected_columns(processed_df)

        # 3) Predecir
        scores = get_prediction(processed_df)

        # 4) Formatear respuesta
        results = []
        for i, s in enumerate(scores):
            s = float(s)
            risk_level = "ALTO" if s > 0.5 else ("MEDIO" if s > 0.25 else "BAJO")
            results.append(
                {
                    "risk_score": s,
                    "risk_level": risk_level,
                    "input_data": input_list[i],
                }
            )
        return results
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error en la predicción batch: {e}")


# Predicción desde CSV
@router.post("/predict/csv")
async def predict_csv(file: UploadFile = File(...)):
    """Predice el riesgo para un CSV completo."""
    if file.content_type != "text/csv":
        raise HTTPException(status_code=400, detail="Tipo de archivo inválido. Se espera text/csv")

    try:
        # 1) Leer CSV
        contents = await file.read()
        buffer = io.StringIO(contents.decode("utf-8"))
        input_df = pd.read_csv(buffer)

        # Validar columnas mínimas
        required = {"comuna", "tipo_accidente", "fecha"}
        if not required.issubset(input_df.columns):
            raise ValueError("El CSV debe contener las columnas 'comuna', 'tipo_accidente' y 'fecha'")

        # 1.5) Armonización
        input_df = _harmonize_df(input_df.copy())

        # 2) Preprocesar
        processed_df = preprocess_data(input_df)

        # 2.5) Alinear columnas
        processed_df = _align_to_expected_columns(processed_df)

        # 3) Predecir
        scores = get_prediction(processed_df)

        # 4) Devolver resultados
        out_df = input_df.copy()
        out_df["risk_score"] = [float(x) for x in scores]
        out_df["risk_level"] = out_df["risk_score"].apply(
            lambda s: "ALTO" if s > 0.5 else ("MEDIO" if s > 0.25 else "BAJO")
        )
        return out_df.to_dict(orient="records")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error procesando el CSV: {e}")


# Ranking de Comunas
@router.get("/comunas/ranking")
async def get_comuna_ranking(limit: int = 5):
    """
    Devuelve un ranking de comunas basado en el AUROC de fairness
    (Datos estimados de un gráfico de métricas).
    """
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
