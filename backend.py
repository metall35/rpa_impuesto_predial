from fastapi import FastAPI, BackgroundTasks, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os

# Importar el script RPA
from rpa_bot import run_rpa

app = FastAPI(title="API RPA Impuesto Predial")

# Configurar CORS (por si el index.html se sirve en otro puerto)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoint principal para servir el HTML
@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

# Endpoint de la API para iniciar el bot
@app.post("/api/generar_factura")
def generar_factura(
    search_type: str = Form(...),
    search_value: str = Form(...),
    phone: str = Form(...),
    email: str = Form(...)
):
    # Dado que el bot usa Playwright sincronamente y toma varios segundos,
    # es mejor ejecutarlo y devolver la respuesta cuando finalice,
    # o usar un BackgroundTask si no queremos que el usuario espere la descarga.
    # En este caso, como el usuario quiere un "Loading", esperaremos a que termine
    # para darle un OK o Error.
    
    print(f"Iniciando proceso RPA para {search_type}: {search_value}")
    
    # Ejecutamos el bot
    result = run_rpa(search_type, search_value, phone, email)
    
    if result["status"] == "success":
        return JSONResponse(status_code=200, content=result)
    else:
        return JSONResponse(status_code=500, content=result)

if __name__ == "__main__":
    import uvicorn
    # Para ejecutar este servidor: python backend.py
    uvicorn.run(app, host="0.0.0.0", port=8000)
