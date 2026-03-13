# auth.py

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id_usuario: int
    nombre: str
    email: str
    rol: str # Usamos str para simplificar la compatibilidad con el Enum de la DB
    estado: str
    ultimo_ingreso: Optional[datetime] = None

    class Config:
        from_attributes = True # Esto permite que Pydantic lea objetos de SQLAlchemy

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse