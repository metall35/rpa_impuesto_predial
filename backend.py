from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os

# Importar el script RPA
from rpa_bot import run_rpa

# Asegurar que el directorio de facturas exista
os.makedirs("facturas_descargadas", exist_ok=True)

app = FastAPI(title="API RPA Impuesto Predial")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir las facturas descargadas como archivos estáticos
app.mount("/facturas", StaticFiles(directory="facturas_descargadas"), name="facturas")

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
    print(f"Iniciando proceso RPA para {search_type}: {search_value}")
    
    # Ejecutamos el bot
    result = run_rpa(search_type, search_value, phone, email)
    
    if result["status"] == "success":
        return JSONResponse(status_code=200, content=result)
    else:
        return JSONResponse(status_code=500, content=result)

# Endpoint para imprimir el archivo desde el servidor
@app.post("/api/imprimir_factura")
def imprimir_factura(filename: str = Form(...)):
    file_path = os.path.join("facturas_descargadas", filename)
    if not os.path.exists(file_path):
        return JSONResponse(status_code=404, content={"status": "error", "message": "El archivo no existe en el servidor."})
    try:
        # Usa la asociación predeterminada de Windows para imprimir el archivo PDF
        os.startfile(file_path, "print")
        print(f"Factura {filename} enviada a la cola de impresión del servidor.")
        return {"status": "success", "message": f"Factura {filename} enviada a imprimir en el servidor."}
    except Exception as e:
        print(f"Error al imprimir en el servidor: {e}")
        return JSONResponse(status_code=500, content={"status": "error", "message": f"Error al imprimir: {str(e)}"})

if __name__ == "__main__":
    import uvicorn
    # Ejecutar servidor en puerto 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
