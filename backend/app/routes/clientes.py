from fastapi import APIRouter, Depends, Query
from app.models.cliente import ClienteCreate, ClienteUpdate
from app.core.security import obtener_usuario_actual
from app.services.cliente_service import (
    crear_cliente_db, obtener_clientes_db, 
    obtener_cliente_por_codigo_db, actualizar_cliente_db, cambiar_estado_cliente_db
)

router = APIRouter(tags=["Clientes"], prefix="/clientes")

@router.post("/crear")
async def crear(cliente: ClienteCreate, user: dict = Depends(obtener_usuario_actual)):
    return crear_cliente_db(cliente, user["id_usuario"])

@router.get("/listar")
async def listar(
    pagina: int = Query(1, ge=1), 
    user: dict = Depends(obtener_usuario_actual)
):
    offset = (pagina - 1) * 10
    return obtener_clientes_db(skip=offset, limit=10)

@router.get("/codigo/{codigo_unico}")
async def obtener_por_codigo(codigo_unico: str, user: dict = Depends(obtener_usuario_actual)):
    cliente = obtener_cliente_por_codigo_db(codigo_unico)
    return cliente

@router.put("/codigo/{codigo_cliente}")
async def actualizar(
    codigo_cliente: str, 
    datos: ClienteUpdate, 
    user: dict = Depends(obtener_usuario_actual)
):
    # Pasamos el código único en lugar del ID numérico
    return actualizar_cliente_db(codigo_cliente, datos, user["id_usuario"])

@router.patch("/codigo/{codigo_cliente}/estado")
async def actualizar_estado(
    codigo_cliente: str, 
    activo: bool, 
    user: dict = Depends(obtener_usuario_actual)
):
    return cambiar_estado_cliente_db(codigo_cliente, activo, user["id_usuario"])