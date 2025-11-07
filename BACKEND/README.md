# HackatonDuocUC

---

Este proyecto implementa una API con **FastAPI** para conectarse a **OpenAI GPT-5**, estructurada de forma profesional, además de dar una solución a el tema de 'Smart Cities' entregada en la hackaton AI Aplicada por Duoc UC 2025.


## Resumen rápido

- Lenguaje: Python
- Framework web: FastAPI
- Cliente OpenAI: `src/gpt_client.py` (usa `python-dotenv` para cargar `.env`)
- Entrypoint de desarrollo: `run.py` (usa `uvicorn`)

## Estructura del proyecto

``` bash
HackatonDuocUC/
├── app/                  # Aplicación FastAPI (punto de entrada)
│   └── main.py
├── api/                  # Rutas / endpoints
│   ├── routes_predict.py
│   └── routes_coach.py
├── src/                  # Código auxiliar / clientes
│   └── gpt_client.py
├── .env                  # Variables de entorno (no versionar)
├── requirements.txt
├── run.py                # Script para arrancar con uvicorn
└── README.md
```

## Endpoints principales

- GET `/` → Mensaje de bienvenida (definido en `app/main.py`).
- POST `/api/predict` → endpoint definido en `api/routes_predict.py` (usa `src.gpt_client.ask_openai`).
- POST `/api/coach` → endpoint definido en `api/routes_coach.py` (genera un plan de coaching usando `ask_openai`).

## Requisitos

- Python 3.10+ recomendado.
- `OPENAI_API_KEY` si vas a usar los endpoints que llaman a OpenAI.
- Crear archivo `.env` con las variables de entorno necesarias.

## Instalación y ejecución (Linux / zsh)

1. Sitúate en la carpeta del proyecto:

```bash
cd ./HackatonDuocUC
```

2. Crear y activar un entorno virtual (recomendado):

```bash
# Activar entorno virtual Linux/Mac
python3 -m venv venv
source venv/bin/activate

ó
# Activar entorno virtual Windows
venv\\Scripts\\activate
```

3. Instalar dependencias:

```bash
pip install -r requirements.txt
```

4. Crear archivo `.env` en la raíz con tu API key (si corresponde):

```env
OPENAI_API_KEY=sk-...   # reemplaza con tu clave real
OPENAI_SYSTEM_PROMPT="Eres un asistente experto en análisis de datos y desarrollo backend. Siempre respondes en español de manera clara y profesional."
```

5. Ejecutar la aplicación (desarrollo):

```bash
python run.py
```

Esto lanza Uvicorn con el app importado desde `app.main`. Alternativamente puedes ejecutar directamente:

```bash
uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=reload_flag)
```

## Probar endpoints (ejemplos)

```bash
# Root
curl http://127.0.0.1:8000/

```

## Construir imagen Docker

```bash
docker-compose up --build -d
```

## Endpoints

```bash
POST /api/predict
```

```bash
{
  "prompt": "string"
}
```

### Response

```bash
{
  "score": 0.85,
  "drivers": [
    {
      "message": "Respuesta generada por OpenAI",
      "tokens": {
        "prompt": 62,
        "completion": 28,
        "total": 90
      }
    }
  ]
}
```

## Infraestructura AWS con Terraform

Para desplegar la aplicación en AWS usando Terraform, sigue estos pasos:

1. Asegúrate de tener Terraform instalado y configurado con tus credenciales de AWS.
2. Navega a la carpeta `infra/` del proyecto.
3. Inicializa Terraform:

```bash
terraform init
```

4. Revisa el plan de despliegue:

```bash
terraform plan
```

5. Aplica el plan para crear los recursos:

```bash
terraform apply
```

## Eliminar infraestructura

Para eliminar los recursos creados en AWS, ejecuta:

```bash
terraform destroy
```

Esto eliminará todas las instancias y recursos asociados creados por Terraform. 