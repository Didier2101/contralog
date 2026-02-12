# app/core/security.py

from app.core.config import settings
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError # Añadimos JWTError
from fastapi import Depends, HTTPException, status # Para la inyección de dependencias
from fastapi.security import OAuth2PasswordBearer

# Configuración para que FastAPI sepa de dónde sacar el token (Header: Authorization)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Funciones de Password (Ya las tienes) ---
def obtener_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verificar_password(password_plano: str, password_hasheado: str) -> bool:
    return pwd_context.verify(password_plano, password_hasheado)

# --- Funciones de JWT ---
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

def crear_token_acceso(data: dict):
    datos_a_encriptar = data.copy()
    expiracion = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    datos_a_encriptar.update({"exp": expiracion})
    return jwt.encode(datos_a_encriptar, SECRET_KEY, algorithm=ALGORITHM)

# --- NUEVA FUNCIÓN: El Validador de Rutas ---
def obtener_usuario_actual(token: str = Depends(oauth2_scheme)):
    """
    Esta función actúa como un escudo. Si el token es inválido,
    detiene la ejecución antes de llegar a la base de datos.
    """
    credenciales_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decodificamos el token usando la misma llave secreta
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id_usuario: str = payload.get("sub")
        rol: str = payload.get("rol")
        
        if id_usuario is None:
            raise credenciales_exception
            
        return {"id_usuario": id_usuario, "rol": rol}
    
    except JWTError:
        raise credenciales_exception