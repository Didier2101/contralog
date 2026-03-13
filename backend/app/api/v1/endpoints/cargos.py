# cargos
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.api import deps
from app.schemas.cargo import CargoCreate, CargoOut, CargoUpdate
from app.services import cargo_service
from app.core.security import obtener_usuario_actual

router = APIRouter()

@router.post("/", response_model=CargoOut)
def crear_nuevo_cargo(
    cargo_in: CargoCreate, 
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(obtener_usuario_actual) # Solo usuarios autenticados
):
    return cargo_service.crear_cargo(db=db, cargo_in=cargo_in)

@router.get("/", response_model=List[CargoOut])
def listar_todos_los_cargos(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = Query(50, le=100)
):
    return cargo_service.listar_cargos(db=db, skip=skip, limit=limit)

@router.get("/{codigo_cargo}", response_model=CargoOut)
def obtener_cargo(
    codigo_cargo: str, 
    db: Session = Depends(deps.get_db)
):
    return cargo_service.obtener_cargo_por_codigo(db=db, codigo_cargo=codigo_cargo)

@router.patch("/{codigo_cargo}", response_model=CargoOut)
def actualizar_cargo(
    codigo_cargo: str,
    cargo_data: CargoUpdate,
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(obtener_usuario_actual)
):
    return cargo_service.actualizar_cargo_por_codigo(
        db=db, 
        codigo_cargo=codigo_cargo, 
        datos=cargo_data
    )