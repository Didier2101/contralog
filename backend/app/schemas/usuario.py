from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from enum import Enum
from datetime import datetime

# 1. ENUMS (Espejo de los modelos para validación de entrada)
class RolUsuario(str, Enum):
    admin = "admin"
    aprobador = "aprobador"
    funcionario = "funcionario"

class EstadoUsuario(str, Enum):
    activo = "activo"
    inactivo = "inactivo"

# --- SCHEMAS DE CARGO (Para anidarlos si es necesario) ---
class CargoBase(BaseModel):
    id_cargo: int
    nombre_cargo: str

    class Config:
        from_attributes = True

# --- SCHEMAS DE USUARIO ---

class UsuarioBase(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    rol: RolUsuario

class UsuarioCreate(UsuarioBase):
    password: str = Field(..., min_length=6)
    id_cargo: Optional[int] = Field(None, description="Obligatorio si el rol es funcionario")

class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=3, max_length=100)
    email: Optional[EmailStr] = None
    rol: Optional[RolUsuario] = None
    id_cargo: Optional[int] = None
    estado: Optional[EstadoUsuario] = None

class UsuarioOut(UsuarioBase):
    id_usuario: int
    codigo_usuario: str
    id_cargo: Optional[int] = None
    estado: EstadoUsuario
    ultimo_ingreso: Optional[datetime] = None
    created_at: datetime
    
    # Esto permite que Pydantic lea los objetos de SQLAlchemy directamente
    class Config:
        from_attributes = True

class UsuarioLogin(BaseModel):
    email: EmailStr
    password: str