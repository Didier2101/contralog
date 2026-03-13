from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.cargo import Cargo
from app.schemas.cargo import CargoCreate
from app.utils.codigos import generar_codigo_cargo
from app.core.errors import DatosDuplicados, ErrorOperacion

def crear_cargo(db: Session, cargo_in: CargoCreate):
    # 1. Validamos que el nombre no exista (Lógica de negocio)
    if db.query(Cargo).filter(Cargo.nombre_cargo == cargo_in.nombre_cargo).first():
        raise DatosDuplicados(f"El cargo '{cargo_in.nombre_cargo}' ya existe.")

    intentos = 0
    max_intentos = 5

    while intentos < max_intentos:
        nuevo_codigo = generar_codigo_cargo()
        
        nuevo_cargo = Cargo(
            codigo_cargo=nuevo_codigo,
            nombre_cargo=cargo_in.nombre_cargo,
            descripcion=cargo_in.descripcion
        )

        try:
            db.add(nuevo_cargo)
            db.commit() # Aquí es donde la DB verifica la unicidad
            db.refresh(nuevo_cargo)
            return nuevo_cargo
        
        except IntegrityError as e:
            db.rollback()
            # Si el error es por el codigo_cargo, reintentamos con uno nuevo
            if "codigo_cargo" in str(e.orig):
                intentos += 1
                continue 
            # Si el error es por otra cosa (ej. nombre_cargo que se nos escapó), lanzamos error
            raise DatosDuplicados("Error de integridad. Verifique los datos.")
    
    # Si después de 5 intentos sigue fallando (improbable pero posible)
    raise ErrorOperacion("No se pudo generar un código de cargo único. Intente de nuevo.")