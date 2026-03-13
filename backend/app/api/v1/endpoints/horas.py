from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.hora import RegistroHoraCreate, RegistroHoraOut
from app.services import hora_service

router = APIRouter()

@router.post("/", response_model=RegistroHoraOut)
def crear_registro_hora(
    hora_in: RegistroHoraCreate, 
    db: Session = Depends(get_db),
    current_user_id: int = 1 # Temporal hasta tener el sistema de Auth con JWT
):
    return hora_service.registrar_tiempo(db, current_user_id, hora_in)