from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.proyecto import ProyectoCreate, ProyectoOut, ProyectoUpdate
from app.services import proyecto_service

router = APIRouter()

@router.post("/", response_model=ProyectoOut)
def crear_nuevo_proyecto(proyecto_in: ProyectoCreate, db: Session = Depends(get_db)):
    """
    Crea una nueva oportunidad o proyecto en el pipeline.
    """
    return proyecto_service.crear_proyecto(db, proyecto_in)

@router.get("/", response_model=List[ProyectoOut])
def listar_proyectos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return proyecto_service.obtener_proyectos(db, skip=skip, limit=limit)

@router.put("/{id_proyecto}", response_model=ProyectoOut)
def actualizar_estado_proyecto(
    id_proyecto: int, 
    proyecto_in: ProyectoUpdate, 
    db: Session = Depends(get_db)
):
    """
    Permite mover el proyecto entre etapas (Prospección -> Negociación -> Ejecución).
    """
    return proyecto_service.actualizar_proyecto(db, id_proyecto, proyecto_in)