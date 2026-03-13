from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.api import deps
from app.schemas.cliente import ClienteCreate, ClienteOut
from app.services import cliente_service
from app.core.security import obtener_usuario_actual
from app.models.cliente import Cliente

router = APIRouter()

@router.post("/", response_model=ClienteOut)
def crear_cliente(
    cliente_in: ClienteCreate, 
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(obtener_usuario_actual)
):
    # Pasamos el id del usuario que está logueado para la auditoría
    return cliente_service.crear_cliente(
        db=db, 
        cliente_in=cliente_in, 
        id_operador=current_user["id_usuario"]
    )

@router.get("/", response_model=List[ClienteOut])
def listar_clientes(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = Query(20, le=100)
):
    return db.query(Cliente).offset(skip).limit(limit).all()

@router.get("/codigo/{codigo_cliente}", response_model=ClienteOut)
def obtener_cliente(
    codigo_cliente: str, 
    db: Session = Depends(deps.get_db)
):
    return cliente_service.obtener_cliente_por_codigo(db, codigo_cliente)


@router.get("/", response_model=List[ClienteOut])
def listar_clientes(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 10,
    current_user: dict = Depends(obtener_usuario_actual)
):
    # Usamos el service para mantener la arquitectura limpia
    return cliente_service.obtener_todos_los_clientes(db=db, skip=skip, limit=limit)