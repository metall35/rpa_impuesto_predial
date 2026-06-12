from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import asyncio
import time
import uuid
import threading

from rpa_bot import run_rpa_start, run_rpa_continue, close_session_objects

os.makedirs("facturas_descargadas", exist_ok=True)

import queue

class RpaThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.cmd_queue = queue.Queue()
        self.resp_queue = queue.Queue()
        self.daemon = True
        self.start()
        
    def run(self):
        from playwright.sync_api import sync_playwright
        print("THREAD DEBUG: Inicializando Playwright y Browser global...")
        with sync_playwright() as p:
            self.playwright = p
            self.browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
            print("THREAD DEBUG: Browser global inicializado exitosamente.")
            while True:
                func, args, kwargs = self.cmd_queue.get()
                if func is None:
                    break
                try:
                    # Inyectar el browser global si la función es run_rpa_start
                    if func.__name__ == 'run_rpa_start':
                        res = func(self.browser, *args, **kwargs)
                    else:
                        res = func(*args, **kwargs)
                    self.resp_queue.put((res, None))
                except Exception as e:
                    self.resp_queue.put((None, e))
                
    def execute(self, func, *args, **kwargs):
        self.cmd_queue.put((func, args, kwargs))
        res, err = self.resp_queue.get()
        if err:
            raise err
        return res
        
    def stop(self):
        self.cmd_queue.put((None, None, None))

# Almacén global de sesiones de navegador abiertas
active_sessions = {}

# Hilo global para reutilización de Playwright
global_rpa_thread = RpaThread()

def cleanup_expired_sessions():
    """Cierra y elimina las sesiones de navegador Playwright inactivas por más de 5 minutos."""
    now = time.time()
    expired = [sid for sid, s in active_sessions.items() if now - s["timestamp"] > 300]
    for sid in expired:
        print(f"Limpieza: Cerrando sesión expirada: {sid}")
        try:
            s = active_sessions[sid]
            global_rpa_thread.execute(close_session_objects, s["session_data"])
        except Exception as e:
            print(f"Error al limpiar sesión expirada {sid}: {e}")
        del active_sessions[sid]

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
            
            # Limpiar sesiones de navegador inactivas
            cleanup_expired_sessions()
            
        except Exception as e:
            print(f"Error durante la limpieza de facturas o sesiones: {e}")
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
    try:
        result = global_rpa_thread.execute(run_rpa_start, search_type, search_value, phone, email)
        
        if result["status"] == "multiple_predios":
            session_id = str(uuid.uuid4())
            session_data = result.pop("session_data")
            session_data["search_value"] = search_value
            active_sessions[session_id] = {
                "session_data": session_data,
                "timestamp": time.time()
            }
            
            return JSONResponse(status_code=200, content={
                "status": "multiple_predios",
                "session_id": session_id,
                "predios": result["predios"]
            })
        elif result["status"] == "success":
            return JSONResponse(status_code=200, content=result)
        else:
            return JSONResponse(status_code=500, content=result)
    except Exception as e:
        raise e

@app.post("/api/seleccionar_predio")
def seleccionar_predio(
    session_id: str = Form(...),
    index: int = Form(...),
    phone: str = Form(...),
    email: str = Form(...)
):
    session_entry = active_sessions.get(session_id)
    if not session_entry:
        return JSONResponse(status_code=404, content={
            "status": "error", 
            "message": "La sesión ha expirado por inactividad. Por favor, vuelva a realizar la búsqueda."
        })
    
    del active_sessions[session_id]
    
    session_data = session_entry["session_data"]
    search_value = session_data.get("search_value", "")
    
    try:
        result = global_rpa_thread.execute(run_rpa_continue, session_data, index, search_value, phone, email)
        
        if result["status"] == "success":
            return JSONResponse(status_code=200, content=result)
        else:
            return JSONResponse(status_code=500, content=result)
    except Exception as e:
        raise e

@app.post("/api/imprimir_factura")
def imprimir_factura(filename: str = Form(...)):
    file_path = os.path.join("facturas_descargadas", filename)
    if not os.path.exists(file_path):
        return JSONResponse(status_code=404, content={"status": "error", "message": "El archivo no existe en el servidor."})
    try:
        if hasattr(os, "startfile"):
            os.startfile(file_path, "print")
            return {"status": "success", "message": f"Factura {filename} enviada a imprimir en el servidor."}
        else:
            print(f"[Linux/Servidor] Comando de impresión simulado para: {file_path}")
            return {"status": "success", "message": f"Factura {filename} simulada (impresión no disponible en Linux sin impresora física configurada)."}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": f"Error al imprimir: {str(e)}"})

app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
