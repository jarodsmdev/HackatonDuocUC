import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes_predict import router as predict_router
from api.routes_coach import router as coach_router
from api.routes_history import router as history_router 
from src.database import init_db

# Agregar el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


app = FastAPI(
    title="HackatonDuocUC API",
    description="API RES  con FastAPI + OpenAI",
    version="1.0.5"
)

# Configuración CORS
origins = [
    "http://localhost:4200",   # React local
    "http://localhost:5173/",   # Alternativa local
    "https://smartcitiesvina.netlify.app/",  # Producción (opcional)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,           # Dominios permitidos
    allow_credentials=True,          # Permitir cookies/autenticación
    allow_methods=["*"],             # Permitir todos los métodos (GET, POST, etc.)
    allow_headers=["*"],             # Permitir todos los headers (Authorization, Content-Type, etc.)
)

# Evento de startup para inicializar la base de datos
@app.on_event("startup")
def startup_event():
    init_db()
    print("Aplicación iniciada - Base de datos lista")

# Rutas
app.include_router(predict_router, prefix="/api/v1")
app.include_router(coach_router, prefix="/api/v1")
app.include_router(history_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "Sistema de Análisis de Accidentes - API funcionando correctamente",
        "endpoints": {
            "predict": "/api/v1/predict",
            "coach": "/api/v1/coach", 
            "history": "/api/v1/history",
            "stats": "/api/v1/stats"
        }
    }