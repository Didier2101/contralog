from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings

# Configuración de Passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuración de OAuth2 - Debe apuntar a la ruta real de tu login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

# Variables de Configuración
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

# --- FUNCIONES DE HASHING ---
def obtener_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verificar_password(password_plano: str, password_hasheado: str) -> bool:
    return pwd_context.verify(password_plano, password_hasheado)

# --- FUNCIONES DE JWT ---
def crear_token_acceso(data: dict):
    datos_a_encriptar = data.copy()
    expiracion = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    datos_a_encriptar.update({"exp": expiracion})
    return jwt.encode(datos_a_encriptar, SECRET_KEY, algorithm=ALGORITHM)

# --- VALIDADOR DE RUTAS (CORREGIDO PARA EVITAR KEYERROR) ---
def obtener_usuario_actual(token: str = Depends(oauth2_scheme)):
    exception_auth = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Sesión inválida o expirada",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Extraemos los datos del token
        id_usuario: str = payload.get("sub")
        email: str = payload.get("email")
        rol: str = payload.get("rol")
        
        if id_usuario is None:
            raise exception_auth
            
        # Devolvemos un diccionario con AMBAS llaves para que ningún endpoint falle
        return {
            "id_usuario": id_usuario, 
            "email": email, 
            "rol": rol
        }
    
    except JWTError:
        raise exception_auth