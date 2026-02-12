from fastapi import APIRouter, Depends, File, UploadFile, Query, Form
from typing import List
from app.models.contrato import ContratoJuridicoCreate, ContratoNaturalCreate, EstadoContrato
from app.core.security import obtener_usuario_actual
from app.services.contrato_service import (
    crear_contrato_juridico_db, 
    obtener_todos_contratos_db, 
    obtener_contrato_por_codigo_db,
    crear_contrato_natural_db,
    obtener_alertas_vencimiento_db
)
from datetime import date

router = APIRouter(tags=["Contratos"], prefix="/contratos")

@router.post("/natural")
async def crear_natural(
    id_cliente: int = Form(...),
    fecha_inicio: date = Form(...),
    fecha_final: date = Form(...),
    nda_firmado: bool = Form(False),
    estado: EstadoContrato = Form(EstadoContrato.pendiente),
    archivo: UploadFile = File(...),
    user: dict = Depends(obtener_usuario_actual)
):
    contrato = ContratoNaturalCreate(
        id_cliente=id_cliente,
        fecha_inicio=fecha_inicio,
        fecha_final=fecha_final,
        nda_firmado=nda_firmado,
        estado=estado,
        creado_por=user["id_usuario"]
    )
    return await crear_contrato_natural_db(contrato, archivo)

@router.post("/juridico")
async def crear_juridico(
    id_cliente: int = Form(...),
    fecha_inicio: date = Form(...),
    fecha_final: date = Form(...),
    estado: EstadoContrato = Form(EstadoContrato.pendiente),
    # Recibimos el archivo principal y las pólizas por separado o en lista
    contrato_pdf: UploadFile = File(...), 
    polizas: List[UploadFile] = File(None), 
    tipos_poliza: List[int] = Form(None), # IDs de la tabla tipo_documentos
    user: dict = Depends(obtener_usuario_actual)
):
    contrato = ContratoJuridicoCreate(
        id_cliente=id_cliente,
        fecha_inicio=fecha_inicio,
        fecha_final=fecha_final,
        estado=estado,
        creado_por=user["id_usuario"]
    )
    return await crear_contrato_juridico_db(contrato, contrato_pdf, polizas, tipos_poliza)

@router.get("/listar")
async def listar(
    pagina: int = Query(1, ge=1),
    user: dict = Depends(obtener_usuario_actual)
):
    offset = (pagina - 1) * 20
    return obtener_todos_contratos_db(limit=20, skip=offset)

@router.get("/{tipo}/{codigo}")
async def detalle(
    tipo: str, 
    codigo: str, # Cambiado de id_contrato: int a codigo: str
    user: dict = Depends(obtener_usuario_actual)
):
    # tipo debe ser 'natural' o 'juridico'
    return obtener_contrato_por_codigo_db(codigo, tipo)


@router.get("/alertas")
async def obtener_alertas(user: dict = Depends(obtener_usuario_actual)):
    # Este endpoint devuelve solo los contratos en riesgo
    return obtener_alertas_vencimiento_db()