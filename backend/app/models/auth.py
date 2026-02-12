# app/models/auth.py

from pydantic import BaseModel, EmailStr
from enum import Enum
from typing import Optional
from datetime import datetime

# 1. Enums: Definen los valores permitidos (vienen de tu DB)
class RolUsuario(str, Enum):
    admin = "admin"
    colaborador = "colaborador"

class EstadoUsuario(str, Enum):
    activo = "activo"
    inactivo = "inactivo"

# 2. Esquemas de Pydantic

# Lo que el usuario escribe en el formulario de Login
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# Los datos del perfil del usuario (Sin la contraseña)
class UserResponse(BaseModel):
    id_usuario: int
    nombre: str
    email: str
    rol: RolUsuario
    estado: EstadoUsuario
    ultimo_ingreso: Optional[datetime] = None

    class Config:
        from_attributes = True

# LA PIEZA FINAL: Lo que la API responde realmente al loguear
# Incluye el token de seguridad y el objeto del usuario
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse  # Aquí usamos el modelo de arriba