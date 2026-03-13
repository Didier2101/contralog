
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api import deps
from app.models.contrato import Contrato    

router = APIRouter()

@router.get("/alertas")
def obtener_alertas_criticas(db: Session = Depends(deps.get_db)):
    return db.query(Contrato).filter(
        Contrato.estado.in_(['por_vencer', 'vencido'])
    ).all()