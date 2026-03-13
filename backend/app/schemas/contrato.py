from pydantic import BaseModel
from datetime import date
from typing import Optional
from enum import Enum

class EstadoContrato(str, Enum):
    vencido = 'vencido'
    activo = 'activo'
    por_vencer = 'por_vencer'
    cancelado = 'cancelado'
    pendiente = 'pendiente'

class ContratoCreate(BaseModel):
    id_cliente: int
    tipo_contrato: str # Ej: "Prestación de Servicios"
    fecha_inicio: date
    fecha_final: date

class ContratoOut(ContratoCreate):
    id_contrato: int
    codigo_unico: str
    estado: EstadoContrato
    creado_por: int
    s3_key_contrato: Optional[str]

    class Config:
        from_attributes = True