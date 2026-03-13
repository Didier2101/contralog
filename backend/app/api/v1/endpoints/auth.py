from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.auth import LoginRequest, TokenResponse
from app.services import auth_service
from app.core.security import crear_token_acceso # Debes tener esta función

router = APIRouter()

@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    usuario = auth_service.login_usuario(db, data.email, data.password)
    
    # IMPORTANTE: Metemos el ID en el 'sub' y el email aparte
    access_token = crear_token_acceso(
        data={
            "sub": str(usuario.id_usuario), 
            "email": usuario.email, 
            "rol": usuario.rol
        }
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": usuario
    }