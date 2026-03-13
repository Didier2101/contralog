from sqlalchemy.orm import Session
from app.models.auditoria import AuditoriaCambio # Asegúrate de tener este modelo
import json

def registrar_cambio_db(
    db: Session, 
    id_usuario: int, 
    accion: str, 
    tabla: str, 
    id_registro: int, 
    detalle: dict
):
    """
    Registra un evento en la tabla de auditoría usando SQLAlchemy.
    """
    try:
        nuevo_log = AuditoriaCambio(
            id_usuario=id_usuario,
            accion=accion,
            tabla_afectada=tabla,
            id_registro_afectado=id_registro,
            detalle_cambio=detalle # SQLAlchemy se encarga de convertir el dict a JSON si el campo es JSON
        )
        db.add(nuevo_log)
        # NOTA: No hacemos db.commit() aquí. 
        # Dejamos que el service principal lo haga para asegurar la atomicidad.
    except Exception as e:
        print(f"Error crítico en auditoría: {e}")
        # En auditoría a veces es mejor no lanzar excepción para no bloquear el negocio,
        # pero para ser 'brutalmente honesto', si la ley te exige auditoría, deberías lanzarla.