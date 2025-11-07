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