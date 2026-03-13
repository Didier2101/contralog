from sqlalchemy.orm import Session
from datetime import datetime
from app.models.usuario import Usuario
from app.core.security import verificar_password
from app.core.errors import CredencialesInvalidas

def login_usuario(db: Session, email: str, password: str):
    # 1. Buscar usuario con SQLAlchemy (Mucho más limpio que un SELECT manual)
    usuario = db.query(Usuario).filter(
        Usuario.email == email, 
        Usuario.estado == 'activo'
    ).first()

    # 2. Validación directa
    if not usuario or not verificar_password(password, usuario.password):
        raise CredencialesInvalidas()

    # 3. Actualizar último ingreso
    usuario.ultimo_ingreso = datetime.now()
    
    # Nota: Si vas a usar una tabla de 'sesiones', deberías crear el modelo 
    # de SQLAlchemy para 'Sesion' y añadir el registro aquí. 
    # Por ahora, mantenemos la actualización del usuario.
    
    db.commit()
    db.refresh(usuario)
    
    return usuario

def logout_usuario(db: Session, usuario_id: int):
    # El logout en aplicaciones con JWT (Stateless) es principalmente del lado del cliente
    # (borrar el token). Pero si quieres registrar el fin de sesión en DB:
    # Aquí deberías buscar la última sesión en tu tabla de sesiones y cerrarla.
    pass