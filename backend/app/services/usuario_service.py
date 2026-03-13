from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.usuario import Usuario
from app.models.cargo import Cargo
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate
from app.core.security import obtener_password_hash
from app.core.errors import RegistroNoEncontrado, DatosDuplicados, ErrorOperacion
from app.utils.codigos import generar_codigo_usuario
from app.services.auditoria_service import registrar_cambio_db

def crear_nuevo_usuario(db: Session, usuario_in: UsuarioCreate):
    """
    Crea un usuario con ORM, genera código único y valida cargos.
    """
    # 1. Validación de Negocio: Funcionario debe tener cargo
    if usuario_in.rol == "funcionario" and not usuario_in.id_cargo:
        raise ErrorOperacion("El rol 'funcionario' requiere asignar un cargo (id_cargo).")

    # 2. Verificar que el cargo exista si se proporcionó
    if usuario_in.id_cargo:
        cargo = db.query(Cargo).filter(Cargo.id_cargo == usuario_in.id_cargo).first()
        if not cargo:
            raise RegistroNoEncontrado("Cargo", usuario_in.id_cargo)

    intentos = 0
    while intentos < 3:
        nuevo_codigo = generar_codigo_usuario()
        
        # 3. Preparar el modelo de base de datos
        db_usuario = Usuario(
            codigo_usuario=nuevo_codigo,
            nombre=usuario_in.nombre,
            email=usuario_in.email,
            password=obtener_password_hash(usuario_in.password),
            rol=usuario_in.rol,
            id_cargo=usuario_in.id_cargo,
            estado="activo"
        )

        try:
            db.add(db_usuario)
            db.commit()
            db.refresh(db_usuario)
            
            # --- AUDITORÍA ---
            registrar_cambio_db(
                db=db, # Ahora pasamos la sesión de SQLAlchemy
                id_usuario=db_usuario.id_usuario,
                accion="CREATE",
                tabla="usuarios",
                id_registro=db_usuario.id_usuario,
                detalle={"mensaje": "Usuario creado", "codigo": nuevo_codigo}
            )
            return db_usuario

        except IntegrityError as e:
            db.rollback()
            if "codigo_usuario" in str(e.orig):
                intentos += 1
                continue
            if "email" in str(e.orig):
                raise DatosDuplicados(f"El email '{usuario_in.email}' ya está registrado.")
            raise ErrorOperacion("Error de integridad al crear el usuario.")

    raise ErrorOperacion("No se pudo generar un código de usuario único tras varios intentos.")


def obtener_usuarios_db(db: Session, skip: int = 0, limit: int = 20):
    return db.query(Usuario).order_by(Usuario.created_at.desc()).offset(skip).limit(limit).all()

def obtener_usuario_por_codigo(db: Session, codigo_usuario: str):
    """
    Busca un usuario por su identidad de negocio (USR-XXXX)
    """
    usuario = db.query(Usuario).filter(Usuario.codigo_usuario == codigo_usuario).first()
    if not usuario:
        # Nota: RegistroNoEncontrado ahora recibe el código, no el ID
        raise RegistroNoEncontrado("Usuario", codigo_usuario)
    return usuario

def actualizar_usuario_por_codigo(db: Session, codigo_usuario: str, datos: UsuarioUpdate, id_operador: int):
    # Primero buscamos por código
    db_usuario = obtener_usuario_por_codigo(db, codigo_usuario)
    
    update_data = datos.model_dump(exclude_unset=True)
    for campo, valor in update_data.items():
        setattr(db_usuario, campo, valor)

    try:
        db.commit()
        db.refresh(db_usuario)
        return db_usuario
    except IntegrityError:
        db.rollback()
        raise DatosDuplicados("Error de integridad al actualizar.")