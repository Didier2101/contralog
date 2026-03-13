from sqlalchemy.orm import Session
from app.models.hora import RegistroHora
from app.schemas.hora import RegistroHoraCreate
from fastapi import HTTPException

def registrar_tiempo(db: Session, id_usuario: int, hora_in: RegistroHoraCreate):
    # Regla de Oro: No más de 24 horas al día (sumando registros previos)
    total_dia = db.query(RegistroHora).filter(
        RegistroHora.id_usuario == id_usuario,
        RegistroHora.fecha_trabajo == hora_in.fecha_trabajo
    ).with_entities(func.sum(RegistroHora.cantidad_horas)).scalar() or 0
    
    if (total_dia + hora_in.cantidad_horas) > 24:
        raise HTTPException(status_code=400, detail="Excede el límite de horas diarias.")

    # Si es proyecto, validar que el ID exista (punto ciego evitado)
    if hora_in.tipo_registro == 'proyecto' and not hora_in.id_proyecto:
        raise HTTPException(status_code=400, detail="Debe especificar un proyecto.")

    nuevo_registro = RegistroHora(
        **hora_in.model_dump(),
        id_usuario=id_usuario,
        estado_aprobacion='pendiente'
    )
    db.add(nuevo_registro)
    db.commit()
    db.refresh(nuevo_registro)
    return nuevo_registro