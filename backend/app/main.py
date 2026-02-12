import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles  # Importación fundamental
from apscheduler.schedulers.background import BackgroundScheduler

from app.core.exceptions import setup_exception_handlers
from app.services.contrato_service import verificar_vencimientos_db

# Importaciones de rutas
from app.routes.auth import router as auth_router
from app.routes.clientes import router as clientes_router
from app.routes.contratos import router as contratos_router
from app.routes.usuarios import router as usuarios_router
from app.routes.auditoria import router as auditoria_router

app = FastAPI(
    title="ContraLog API Professional",
    description="Gestión de contratos con arquitectura limpia",
    version="1.0.0"
)

# --- CONFIGURACIÓN DE ARCHIVOS ESTÁTICOS ---
# Esto permite que los archivos en la carpeta 'uploads' sean accesibles vía URL
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Montamos la carpeta para que http://localhost:8000/uploads/ sea la puerta de entrada
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# --- PROGRAMADOR DE TAREAS (CRON JOB) ---
scheduler = BackgroundScheduler()
scheduler.add_job(verificar_vencimientos_db, 'cron', hour=0, minute=0)

@app.on_event("startup")
def start_scheduler():
    if not scheduler.running:
        scheduler.start()

@app.on_event("shutdown")
def stop_scheduler():
    scheduler.shutdown()

# --- CONFIGURACIÓN DE MIDDLEWARE Y EXCEPCIONES ---
setup_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# --- INCLUSIÓN DE RUTAS ---
app.include_router(auth_router)
app.include_router(clientes_router)
app.include_router(contratos_router)
app.include_router(usuarios_router)
app.include_router(auditoria_router, prefix="/auditoria", tags=["Auditoría"])

@app.get("/", tags=["Root"])
async def root():
    return {"message": "API de ContraLog activa"}