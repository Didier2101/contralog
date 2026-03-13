from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from enum import Enum
from datetime import datetime

class TipoPersona(str, Enum):
    natural = "natural"
    juridica = "juridica"

class TipoIdentificacion(str, Enum):
    NIT = "NIT"
    CC = "CC"
    CE = "CE"
    RUT = "RUT"

class ClienteBase(BaseModel):
    nombre_razon_social: str = Field(..., min_length=3, max_length=150)
    tipo_persona: TipoPersona
    tipo_identificacion: TipoIdentificacion
    identificacion_fiscal: str = Field(..., min_length=5, max_length=20)
    email_contacto: Optional[EmailStr] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None

class ClienteCreate(ClienteBase):
    pass

# ESTA ES LA CLASE QUE TE FALTA:
class ClienteUpdate(BaseModel):
    nombre_razon_social: Optional[str] = None
    email_contacto: Optional[EmailStr] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    estado: Optional[str] = None # 'activo' o 'inactivo'

class ClienteOut(ClienteBase):
    id_cliente: int
    codigo_cliente: str
    estado: str
    created_at: datetime

    class Config:
        from_attributes = True