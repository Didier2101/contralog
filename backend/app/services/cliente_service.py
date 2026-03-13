from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.cliente import Cliente
from app.models.usuario import Usuario
from app.schemas.cliente import ClienteCreate, ClienteUpdate
from app.utils.codigos import generar_codigo_cliente
from app.core.errors import RegistroNoEncontrado, DatosDuplicados, ErrorOperacion
from app.services.auditoria_service import registrar_cambio_db

def crear_cliente(db: Session, cliente_in: ClienteCreate, id_operador: int):
    # 1. Validación preventiva: Identificación única
    if db.query(Cliente).filter(Cliente.identificacion_fiscal == cliente_in.identificacion_fiscal).first():
        raise DatosDuplicados(f"La identificación {cliente_in.identificacion_fiscal} ya está registrada.")

    intentos = 0
    while intentos < 5:
        nuevo_codigo = generar_codigo_cliente()
        db_cliente = Cliente(
            codigo_cliente=nuevo_codigo,
            **cliente_in.model_dump()
        )

        try:
            db.add(db_cliente)
            db.commit()
            db.refresh(db_cliente)

            # --- AUDITORÍA ---
            registrar_cambio_db(
                db=db,
                id_usuario=id_operador,
                accion="CREATE",
                tabla="clientes",
                id_registro=db_cliente.id_cliente,
                detalle={"codigo": nuevo_codigo, "nombre": db_cliente.nombre_razon_social}
            )
            return db_cliente

        except IntegrityError as e:
            db.rollback()
            if "codigo_cliente" in str(e.orig):
                intentos += 1
                continue
            raise ErrorOperacion("Error de integridad al registrar el cliente.")

    raise ErrorOperacion("Fallo crítico al generar código único de cliente.")

def obtener_todos_los_clientes(db: Session, skip: int = 0, limit: int = 20):
    return db.query(Cliente).offset(skip).limit(limit).all() 


def obtener_cliente_por_codigo(db: Session, codigo_cliente: str):
    # Usamos joinedload o simplemente confiamos en las relaciones de SQLAlchemy
    cliente = db.query(Cliente).filter(Cliente.codigo_cliente == codigo_cliente).first()
    if not cliente:
        raise RegistroNoEncontrado("Cliente", codigo_cliente)
    return cliente

def actualizar_cliente(db: Session, codigo_cliente: str, datos: ClienteUpdate, id_operador: int):
    db_cliente = obtener_cliente_por_codigo(db, codigo_cliente)
    
    update_data = datos.model_dump(exclude_unset=True)
    for campo, valor in update_data.items():
        setattr(db_cliente, campo, valor)

    try:
        db.commit()
        db.refresh(db_cliente)
        
        registrar_cambio_db(
            db=db,
            id_usuario=id_operador,
            accion="UPDATE",
            tabla="clientes",
            id_registro=db_cliente.id_cliente,
            detalle={"cambios": list(update_data.keys())}
        )
        return db_cliente
    except IntegrityError:
        db.rollback()
        raise DatosDuplicados("La actualización entra en conflicto con datos existentes.")

def cambiar_estado_cliente(db: Session, codigo_cliente: str, nuevo_estado: str, id_operador: int):
    db_cliente = obtener_cliente_por_codigo(db, codigo_cliente)
    db_cliente.estado = nuevo_estado
    
    db.commit()
    registrar_cambio_db(
        db=db,
        id_usuario=id_operador,
        accion="STATUS_CHANGE",
        tabla="clientes",
        id_registro=db_cliente.id_cliente,
        detalle={"nuevo_estado": nuevo_estado}
    )
    return db_cliente