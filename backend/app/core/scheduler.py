from sqlalchemy.orm import Session
from app.models.contrato import Contrato
from datetime import date, timedelta

def ejecutar_auditoria_vencimientos(db: Session):
    hoy = date.today()
    alerta_vencimiento = hoy + timedelta(days=15) # Parametrizable

    # 1. Pasar a 'vencido' lo que ya pasó
    db.query(Contrato).filter(
        Contrato.fecha_final < hoy,
        Contrato.estado != 'vencido'
    ).update({"estado": "vencido"})

    # 2. Pasar a 'por_vencer' lo que vence en los próximos 15 días
    db.query(Contrato).filter(
        Contrato.fecha_final.between(hoy, alerta_vencimiento),
        Contrato.estado == 'activo'
    ).update({"estado": "por_vencer"})

    db.commit()