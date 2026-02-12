from datetime import datetime, date
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from enum import Enum

# --- 1. ENUMS ---
class EstadoContrato(str, Enum):
    vencido = "vencido"
    activo = "activo"
    por_vencer = "por_vencer"
    cancelado = "cancelado"
    pendiente = "pendiente"

class TipoPersona(str, Enum):
    natural = "natural"
    juridica = "juridica"

# --- 2. MODELOS DE APOYO (DOCUMENTOS Y CONTRATOS) ---
class DocumentoRelacionado(BaseModel):
    codigo: str
    tipo: str
    url: str = Field(..., alias="s3_key")

    class Config:
        from_attributes = True
        populate_by_name = True

class ContratoRelacionado(BaseModel):
    codigo_unico: str
    fecha_inicio: date
    fecha_final: date
    estado: EstadoContrato
    documentos: List[DocumentoRelacionado] = []

    class Config:
        from_attributes = True

# --- 3. MODELO BASE ---
class ClienteBase(BaseModel):
    tipo_persona: TipoPersona
    tipo_identificacion: str
    identificacion: str = Field(..., min_length=5, max_length=20)
    nombre_o_razon_social: str = Field(..., min_length=3, max_length=150)
    telefono: Optional[str] = None
    email_contacto: Optional[EmailStr] = None

# --- 4. MODELOS DE ACCIÓN (LOS QUE FALTABAN) ---
class ClienteCreate(ClienteBase):
    """Modelo para recibir datos en el POST /clientes"""
    activo: bool = True
    creado_por: Optional[int] = None

class ClienteUpdate(BaseModel):
    """Modelo para actualizaciones parciales en PUT/PATCH"""
    tipo_persona: Optional[TipoPersona] = None
    tipo_identificacion: Optional[str] = None
    identificacion: Optional[str] = None
    nombre_o_razon_social: Optional[str] = None
    telefono: Optional[str] = None
    email_contacto: Optional[EmailStr] = None
    activo: Optional[bool] = None

# --- 5. MODELO DE RESPUESTA VISTA 360 ---
class ClienteResponse(ClienteBase):
    id_cliente: int
    codigo_unico: str
    activo: bool
    nombre_creador: Optional[str] = None
    # Cambiamos List[ContratoRelacionado] por List[str]
    contratos_naturales: List[str] = []
    contratos_juridicos: List[str] = []


    class Config:
        from_attributes = True