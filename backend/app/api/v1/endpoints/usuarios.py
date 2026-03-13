from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.api import deps # Donde definiremos get_db
from app.schemas.usuario import UsuarioCreate, UsuarioOut, UsuarioUpdate, UsuarioLogin
from app.services import usuario_service
from app.core.security import obtener_usuario_actual

router = APIRouter()

# POST /usuarios/
@router.post("/", response_model=UsuarioOut)
def registrar_usuario(
    usuario_in: UsuarioCreate, 
    db: Session = Depends(deps.get_db)
):
    return usuario_service.crear_nuevo_usuario(db=db, usuario_in=usuario_in)

# GET /usuarios/
@router.get("/", response_model=List[UsuarioOut])
def listar_usuarios(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = Query(20, le=100)
):
    return usuario_service.obtener_usuarios_db(db=db, skip=skip, limit=limit)

# GET /usuarios/USR-2026-A1B2
@router.get("/{codigo_usuario}", response_model=UsuarioOut)
def obtener_usuario(
    codigo_usuario: str, 
    db: Session = Depends(deps.get_db)
):
    return usuario_service.obtener_usuario_por_codigo(db=db, codigo_usuario=codigo_usuario)

# PATCH /usuarios/USR-2026-A1B2
@router.patch("/{codigo_usuario}", response_model=UsuarioOut)
def actualizar_usuario(
    codigo_usuario: str, 
    usuario_data: UsuarioUpdate,
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(obtener_usuario_actual)
):
    return usuario_service.actualizar_usuario_por_codigo(
        db=db, 
        codigo_usuario=codigo_usuario, 
        datos=usuario_data, 
        id_operador=current_user["id_usuario"]
    )