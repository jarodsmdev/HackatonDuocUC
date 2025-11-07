Hackaton 2025 - CITT
=====================


Este repositorio contiene el código fuente para la API de predicción de riesgo de accidentes de tráfico, desarrollada como parte de la Hackaton 2025 organizada por CITT.

Estructura del Proyecto
---------------------

- `BACKEND/`: Contiene el código fuente de la API construida con FastAPI.
  - `api/`: Define las rutas y endpoints de la API.
  - `src/`: Contiene la lógica de procesamiento de datos y modelos de machine learning.
- `models/`: Almacena los modelos de machine learning entrenados.
- `README.md`: Documentación del proyecto.
- `requirements.txt`: Lista de dependencias necesarias para ejecutar la API.
- `.env`: Archivo de configuración para variables de entorno (no incluido en el repositorio por seguridad).
- `Dockerfile`: Configuración para contenerizar la aplicación.
- `docker-compose.yml`: Configuración para orquestar servicios Docker si es necesario.
- `FRONTEND/`: (Opcional) Código fuente para la interfaz de usuario si aplica.
- `notebooks/`: Notebooks de Jupyter utilizados para análisis exploratorio y desarrollo de modelos.

Notebook Jupyter en Colab
--------------------------
Puedes acceder al notebook Jupyter utilizado para el análisis exploratorio y desarrollo de modelos en Google Colab a través del siguiente enlace:
[Notebook Jupyter en Colab](https://colab.research.google.com/drive/1NDXIipgJK-YuEvBtVvULcF3haBphV2lt?usp=sharing)

Pruebas iniciales de entrenamiento de modelos y análisis del proyecto y análisis exploratorio se encuentran en este notebook.

Instalación
------------
1. Clona el repositorio:
   ```bash
   git clone  
   ```

2. Navega al directorio del proyecto:
   ```bash
   cd BACKEND
   ```

3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ``` 
4. Configura las variables de entorno en un archivo `.env` basado en el archivo `.env.example`.
5. Inicia la API:
   ```bash
   python run.py
   ```

Uso
---
Una vez que la API esté en funcionamiento, puedes acceder a la documentación interactiva en:

```
http://localhost:8000/docs
```
Links utiles de data:
- [Repositorio de datos de accidentes de tráfico en Chile](https://ideocuc-ocuc.hub.arcgis.com/datasets/bbc4e4f6fc3a4490ae7dac787b90dafd_0/explore?location=-33.620611%2C-70.738368%2C9.93)
- [Repositorio alternativo de datos de accidentes de tráfico en Chile](https://mapas-conaset.opendata.arcgis.com/search
  
Como esta desplegado frontend:
- [Frontend desplegado en Netlify](https://smartcitiesvina.netlify.app/)
- [Enlace a Trello](https://trello.com/b/MjF4hXZK/sprint-smart-cities)

## Informe técnico

#### Backend
•	Lenguaje: Python
•	Framework web: FastAPI
•	Servidor ASGI: Uvicorn
•	Cliente OpenAI: openai (encapsulado en src/gpt_client.py)
•	Carga de variables de entorno: python-dotenv (.env)
•	Gestión CORS: CORSMiddleware (en app/main.py)
•	Concurrencia: asyncio (uso de asyncio.to_thread en /api/coach)
•	Entrypoint dev: run.py
•	Endpoints principales: POST /api/predict, POST /api/coach
•	Docker: Dockerfile + docker-compose.yml (usa env_file: .env)
•	Dependencias: requirements.txt
•	Estructura clave: app/main.py, api/routes_predict.py, api/routes_coach.py, src/gpt_client.py, .env, run.py, Dockerfile

### Frontend

* Lenguaje: TypeScript
* Framework UI: React
* Bundler / Dev server: Vite (dev port: 5173)
* Entrypoint: main.tsx → monta App.tsx
* Estilos: CSS global (src/styles.css) + variables de tema (src/theme.tsx)
* Modos de tema: claro / oscuro / daltónico (Okabe–Ito) — guardado en localStorage
* Mapas: Leaflet + react-leaflet (componente: src/components/MapView.tsx)
* Gráficas / KPIs: Recharts
* Reportes / PDF: jsPDF + jspdf-autotable (src/utils/report.ts)
* STT / TTS: Web Speech API (SpeechRecognition) y speechSynthesis (implementado en src/components/AgentQuery.tsx)
* Utilidades: funciones compartidas en utils.ts y tipos en types.ts
* Componentes principales: Navbar, AgentQuery, AgentProposals, CriticalRoutesTable, TemporalAnalysis (src/components/)
* Scripts npm: dev (vite), build (tsc -b && vite build), preview (vite) — package.json
* Salida de build: index.html y dist/assets (generado por vite build)
* Estructura clave: src/main.tsx, src/App.tsx, src/theme.tsx, src/styles.css, src/components/, report.ts
* Cómo ejecutar: npm install && npm run dev (abrir http://localhost:5173)