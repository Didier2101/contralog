import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from apscheduler.schedulers.background import BackgroundScheduler

from app.api.v1.api import api_router 
from app.database import engine, Base, SessionLocal # Necesitamos SessionLocal para el scheduler
from app.models import usuario, cargo, cliente, contrato, documento # IMPORTAR TODOS
from app.services.contrato_service import verificar_vencimientos # El nuevo nombre sin _db

# 1. Crear tablas
Base.metadata.create_all(bind=engine)

# 2. Configurar el Scheduler profesionalmente
scheduler = BackgroundScheduler()

def tarea_vencimientos():
    """Función puente para darle una sesión de DB al service"""
    db = SessionLocal()
    try:
        verificar_vencimientos(db)
        print("Auditoría de vencimientos ejecutada con éxito.")
    finally:
        db.close()

# Programar para que corra cada medianoche
scheduler.add_job(tarea_vencimientos, 'cron', hour=0, minute=0)

app = FastAPI(
    title="ContraLog API Professional",
    description="Gestión de contratos con arquitectura limpia y ORM",
    version="1.1.0"
)

# --- ARCHIVOS ESTÁTICOS ---
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# --- EVENTOS DE CICLO DE VIDA ---
@app.on_event("startup")
def startup_event():
    if not scheduler.running:
        scheduler.start()

@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()

# --- MIDDLEWARE ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- RUTAS ---
app.include_router(api_router, prefix="/api/v1")

@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "API de ContraLog activa",
        "docs": "/docs",
        "version": "1.1.0 (ORM Enabled)"
    }