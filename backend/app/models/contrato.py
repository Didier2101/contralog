from pydantic import BaseModel
from datetime import date
from typing import Optional
from enum import Enum

class EstadoContrato(str, Enum):
    vencido = "vencido"
    activo = "activo"
    por_vencer = "por_vencer"
    cancelado = "cancelado"
    pendiente = "pendiente"

class ContratoBase(BaseModel):
    id_cliente: int
    fecha_inicio: date
    fecha_final: date
    estado: Optional[EstadoContrato] = EstadoContrato.pendiente
    creado_por: Optional[int] = None

class ContratoNaturalCreate(ContratoBase):
    nda_firmado: bool = False
    s3_key_terminos_condiciones: Optional[str] = None

class ContratoJuridicoCreate(ContratoBase):
    s3_key_terminos_condiciones: Optional[str] = None

# Nuevo modelo para representar los documentos en la respuesta
class DocumentoContrato(BaseModel):
    codigo_seguimiento: str
    id_tipo_doc: int
    s3_key: str