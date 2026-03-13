from sqlalchemy.orm import Session
from app.models.proyecto import Proyecto
from app.schemas.proyecto import ProyectoCreate, ProyectoUpdate
from fastapi import HTTPException

def crear_proyecto(db: Session, proyecto_in: ProyectoCreate):
    # Verificamos si el cliente existe antes de crear la oportunidad
    nuevo_proyecto = Proyecto(**proyecto_in.model_dump())
    db.add(nuevo_proyecto)
    db.commit()
    db.refresh(nuevo_proyecto)
    return nuevo_proyecto

def actualizar_proyecto(db: Session, id_proyecto: int, proyecto_in: ProyectoUpdate):
    db_proyecto = db.query(Proyecto).filter(Proyecto.id_proyecto == id_proyecto).first()
    if not db_proyecto:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    
    update_data = proyecto_in.model_dump(exclude_unset=True)
    
    # Lógica Senior: Si el proyecto pasa a 'ejecucion', debería tener un contrato asociado
    if update_data.get("etapa") == "ejecucion" and not db_proyecto.id_contrato:
        if not update_data.get("id_contrato"):
            raise HTTPException(
                status_code=400, 
                detail="No se puede pasar a ejecución sin un contrato vinculado."
            )
            
    for field, value in update_data.items():
        setattr(db_proyecto, field, value)
    
    db.commit()
    db.refresh(db_proyecto)
    return db_proyecto

def obtener_proyectos(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Proyecto).offset(skip).limit(limit).all()