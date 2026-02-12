# app/routes/auth.py

from fastapi import APIRouter
from app.models.auth import LoginRequest, TokenResponse 
from app.services.auth_service import login_usuario_db, logout_usuario_db
from app.core.security import crear_token_acceso

router = APIRouter(tags=["Autenticación"], prefix="/auth")

@router.post("/login", response_model=TokenResponse)
async def login(datos: LoginRequest):
    # Si falla, el servicio lanza CredencialesInvalidas y FastAPI responde 401 automáticamente
    usuario_db = login_usuario_db(datos.email, datos.password)
    
    # La ruta solo se encarga de la "envoltura" del Token
    token_data = {"sub": str(usuario_db["id_usuario"]), "rol": usuario_db["rol"]}
    access_token = crear_token_acceso(data=token_data)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": usuario_db
    }

@router.post("/logout/{id_usuario}")
async def logout(id_usuario: int):
    logout_usuario_db(id_usuario)
    return {"mensaje": "Sesión cerrada correctamente"}