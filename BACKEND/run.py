import os
from dotenv import load_dotenv

# Carga las variables del archivo .env ANTES de que se importe el resto
load_dotenv()

import uvicorn

if __name__ == "__main__":
    reload_flag = True
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=reload_flag)
