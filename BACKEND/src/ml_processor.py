# src/ml_processor.py
import joblib
import pandas as pd
import numpy as np
from pydantic import BaseModel
from typing import List, Dict, Any
from pathlib import Path

# --- Variables Globales para Modelos ---
model_lreg = None
model_rf = None
scaler = None
model_artifacts = {}
metrics = {
    "auroc": 0.88,  # Tomado de tu reporte_metricas.pdf
    "auprc": 0.36,  # Tomado de tu reporte_metricas.pdf
    "brier_score": None # Tu script lo calcula, pero no lo reporta
}
models_loaded = []

# --- Modelos Pydantic para la data ---
# Esto define la entrada para una predicción
class AccidentInput(BaseModel):
    comuna: float
    region: str
    tipo_accidente: str
    leves: int = 0
    fecha: str # Espera formato "YYYY-MM-DD"
    clase_accid: str = "Accidente"

# Esto define la entrada para el endpoint batch
class BatchInput(BaseModel):
    accidents: List[AccidentInput]


def load_models(model_path: Path = Path("models/")):
    """
    Carga todos los artefactos del modelo (.joblib) en memoria
    al iniciar la API.
    """
    global model_lreg, model_rf, scaler, model_artifacts

    # Convertir a Path object
    model_path = Path(model_path)
    
    try:
        model_lreg = joblib.load(model_path / "modelo_lreg.joblib")
        model_rf = joblib.load(model_path / "modelo_rf.joblib")
        scaler = joblib.load(model_path / "scaler.joblib")
        model_artifacts = joblib.load(model_path / "model_artifacts.joblib")
        
        models_loaded = [
            type(model_lreg).__name__,
            type(model_rf).__name__
        ]
        print("✅ Modelos, scaler y artefactos cargados correctamente.")
        
    except FileNotFoundError as e:
        print(f"🚨 ERROR FATAL: No se encontraron los archivos del modelo en '{model_path}'. {e}")
        print("Asegúrate de ejecutar 'train_evaluate.py' primero.")
        # En un escenario real, esto debería impedir que la app inicie
        models_loaded = ["Error al cargar"]


def preprocess_data(data: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocesa el DataFrame de entrada (de la API) para que coincida
    con los datos de entrenamiento.
    """
    if not model_artifacts:
        raise ValueError("Los artefactos del modelo no están cargados.")

    # Extraer listas de columnas guardadas
    CAT_COLS = model_artifacts.get('cat_cols', [])
    NUM_COLS = model_artifacts.get('num_cols', [])
    FEATURE_COLS_POST_DUMMIES = model_artifacts.get('feature_cols_post_dummies', [])

    # --- 1. Renombrar columnas (como en tu script) ---
    # El Pydantic model ya fuerza los nombres correctos (comuna -> Comuna, etc.)
    # Pero los normalizamos para el preprocesamiento
    rename_map = {
        "comuna": "Comuna",
        "region": "Región",
        "tipo_accidente": "TipoAccidente"
    }
    data = data.rename(columns=rename_map)

    if "Claseaccid" not in data.columns:
        data["Claseaccid"] = "Accidente"  # valor por defecto
        print("🔍 Claseaccid creada con valor por defecto")

    # Y si está en CAT_COLS, asegurarse de que existe
    if "Claseaccid" not in CAT_COLS and "Claseaccid" in data.columns:
        CAT_COLS.append("Claseaccid")


    # --- 2. Ingeniería de Fechas (como en tu script) ---
    data["Fecha"] = pd.to_datetime(data["fecha"], errors='coerce')
    data["Año"] = data["Fecha"].dt.year.fillna(2021).astype(int)
    data["Mes"] = data["Fecha"].dt.month.fillna(1).astype(int)
    data["DiaSemana"] = data["Fecha"].dt.dayofweek.fillna(0).astype(int)

    # --- 3. Escalar Numéricas (como en tu script) ---
    # Asegurarse de que todas las columnas numéricas existan
    for col in NUM_COLS:
        if col not in data.columns:
            data[col] = 0 # Valor por defecto
    
    # Aplicar el scaler GUARDADO
    data[NUM_COLS] = scaler.transform(data[NUM_COLS])

    # Convertir Comuna a string para que get_dummies funcione
    if "Comuna" in data.columns:
        data["Comuna"] = "Comuna_" + data["Comuna"].astype(str)
        print("🔍 Comuna convertida a string:", data["Comuna"].iloc[0])

    # Luego aplicar dummies normal
    data[CAT_COLS] = data[CAT_COLS].fillna("desconocido")
    processed_df = pd.get_dummies(data[CAT_COLS + NUM_COLS])

    # --- 4. Dummies Categóricas (como en tu script) ---
    # DEBUG NUCLEAR
    print("="*50)
    print("🔍 DEBUG - PREPROCESAMIENTO")
    print("🔍 Comuna value:", data["Comuna"].iloc[0] if "Comuna" in data.columns else "NO EXISTE")
    print("🔍 Comuna dtype:", data["Comuna"].dtype if "Comuna" in data.columns else "NO EXISTE")
    print("🔍 CAT_COLS:", CAT_COLS)
    
    # Aplicar dummies
    data[CAT_COLS] = data[CAT_COLS].fillna("desconocido")
    processed_df = pd.get_dummies(
    data[CAT_COLS + NUM_COLS], 
    prefix=['' if col == 'Comuna' else col for col in CAT_COLS],
    prefix_sep=''
    )
    
    print("🔍 Columnas generadas después de dummies:")
    for col in processed_df.columns:
        if "Comuna" in col:
            print(f"   - {col}")
    
    print("🔍 Columnas que espera el modelo:")
    for col in FEATURE_COLS_POST_DUMMIES:
        if "Comuna_" in col:
            print(f"   - {col}")
            break  # solo mostrar una para ejemplo
    
    print("="*50)
    
    # --- 5. Alinear Columnas (Crucial) ---
    # Reindexa el DF para que tenga EXACTAMENTE las mismas columnas
    # que el modelo espera, rellenando las faltantes con 0.
    final_df = processed_df.reindex(columns=FEATURE_COLS_POST_DUMMIES, fill_value=0)
    
    return final_df


def get_prediction(data: pd.DataFrame) -> np.ndarray:
    """
    Toma un DataFrame preprocesado y devuelve el score del ensamble.
    """
    if not all([model_lreg, model_rf]):
         raise ValueError("Los modelos no están cargados.")

    # 1. Predecir con ambos modelos
    p_lreg = model_lreg.predict_proba(data)[:, 1]
    p_rf = model_rf.predict_proba(data)[:, 1]
    
    # 2. Ensamble (como en tu script)
    p_blend = 0.5 * p_lreg + 0.5 * p_rf
    
    return p_blend