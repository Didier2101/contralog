from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Any
from enum import Enum
from datetime import datetime

# 1. Enums (Deben estar aquí para que los modelos de abajo los usen)
class RolUsuario(str, Enum):
    admin = "admin"
    colaborador = "colaborador"

class EstadoUsuario(str, Enum):
    activo = "activo"
    inactivo = "inactivo"

# --- ESQUEMAS PARA DETALLES DE ACTIVIDAD ---
class SesionDetalle(BaseModel):
    id_sesion: int
    fecha_ingreso: datetime
    fecha_salida: Optional[datetime]
    duracion_minutos: Optional[int]

class AuditoriaDetalle(BaseModel):
    id_log: int
    accion: str
    tabla_afectada: str
    id_registro_afectado: int
    detalle_cambio: Optional[Any]
    fecha_cambio: datetime

class ClienteResumen(BaseModel):
    id_cliente: int
    nombre_o_razon_social: str
    identificacion: str
    codigo_unico: Optional[str]

# --- ESQUEMAS PRINCIPALES DE USUARIO ---

class UsuarioCreate(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)
    rol: RolUsuario = RolUsuario.colaborador

class UsuarioOut(BaseModel):
    id_usuario: int
    nombre: str
    email: str
    rol: RolUsuario
    estado: EstadoUsuario  # <-- AQUÍ ES DONDE SE USA EL ENUM PARA LA RESPUESTA
    ultimo_ingreso: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UsuarioLogin(BaseModel):
    email: EmailStr
    password: str

class UsuarioDetalladoOut(UsuarioOut):
    historial_sesiones: List[SesionDetalle] = []
    actividad_auditoria: List[AuditoriaDetalle] = []
    clientes_registrados: List[ClienteResumen] = []

class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=3, max_length=100)
    email: Optional[EmailStr] = None
    rol: Optional[RolUsuario] = None
    estado: Optional[EstadoUsuario] = None 

class UsuarioEstadoUpdate(BaseModel):
    nuevo_estado: EstadoUsuario