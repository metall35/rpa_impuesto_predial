from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import asyncio
import time

from rpa_bot import run_rpa

os.makedirs("facturas_descargadas", exist_ok=True)

async def cleanup_old_invoices():
    while True:
        try:
            directory = "facturas_descargadas"
            if os.path.exists(directory):
                now = time.time()
                for filename in os.listdir(directory):
                    if filename.endswith(".pdf"):
                        file_path = os.path.join(directory, filename)
                        if os.path.isfile(file_path):
                            file_age = now - os.path.getmtime(file_path)
                            if file_age > 1800:
                                os.remove(file_path)
                                print(f"Limpieza: Factura antigua eliminada: {filename} (antigüedad: {file_age:.1f}s)")
        except Exception as e:
            print(f"Error durante la limpieza de facturas: {e}")
        await asyncio.sleep(120)

app = FastAPI(title="API RPA Impuesto Predial")

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(cleanup_old_invoices())

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/facturas", StaticFiles(directory="facturas_descargadas"), name="facturas")

@app.post("/api/generar_factura")
def generar_factura(
    search_type: str = Form(...),
    search_value: str = Form(...),
    phone: str = Form(...),
    email: str = Form(...)
):
    result = run_rpa(search_type, search_value, phone, email)
    
    if result["status"] == "success":
        return JSONResponse(status_code=200, content=result)
    else:
        return JSONResponse(status_code=500, content=result)


app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
