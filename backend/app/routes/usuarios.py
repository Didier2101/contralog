from fastapi import APIRouter, Depends
from app.models.usuario import UsuarioCreate, UsuarioOut, UsuarioDetalladoOut, UsuarioUpdate, UsuarioEstadoUpdate
from app.core.security import obtener_usuario_actual
from typing import List
from app.services.usuario_service import (
    crear_nuevo_usuario, obtener_usuarios_db, 
    obtener_usuario_completo_db, actualizar_usuario_db, cambiar_estado_usuario_db
)

router = APIRouter(tags=["Usuarios"], prefix="/usuarios")

@router.post("/crear", response_model=UsuarioDetalladoOut)
async def registrar_usuario(usuario: UsuarioCreate):
    return crear_nuevo_usuario(usuario)

@router.get("/listar", response_model=List[UsuarioOut])
async def listar_usuarios(limit: int = 20, offset: int = 0):
    return obtener_usuarios_db(limit=limit, offset=offset)

@router.get("/{id_usuario}", response_model=UsuarioDetalladoOut)
async def obtener_usuario(id_usuario: int):
    return obtener_usuario_completo_db(id_usuario)

@router.patch("/{id_usuario}", response_model=UsuarioDetalladoOut)
async def actualizar_usuario(id_usuario: int, usuario_data: UsuarioUpdate):
    datos = usuario_data.model_dump(exclude_unset=True)
    return actualizar_usuario_db(id_usuario, datos)


@router.put("/{id_usuario}/estado")
async def actualizar_estado(
    id_usuario: int, 
    datos: UsuarioEstadoUpdate, 
    user: dict = Depends(obtener_usuario_actual) 
):
   
    return cambiar_estado_usuario_db(id_usuario, datos.nuevo_estado.value, user["id_usuario"])