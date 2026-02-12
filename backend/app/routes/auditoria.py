from fastapi import APIRouter, Depends, Query, HTTPException, status # Añadimos HTTPException y status
from typing import List
from app.models.auditoria import AuditoriaOut
from app.services.auditoria_service import obtener_logs_auditoria_db
from app.core.security import obtener_usuario_actual

router = APIRouter(tags=["Auditoría"])

@router.get("/logs", response_model=List[AuditoriaOut])
async def listar_logs(
    limit: int = Query(5, le=100),
    user: dict = Depends(obtener_usuario_actual)
):
    # Verificamos si el usuario tiene el rol de admin
    if user.get("rol") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No autorizado para ver los logs de auditoría"
        )
    
    return obtener_logs_auditoria_db(limit)