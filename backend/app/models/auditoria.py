from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any, Dict

class AuditoriaOut(BaseModel):
    id_log: int
    id_usuario: Optional[int]
    usuario_nombre: Optional[str] = None # Para facilitar la vista al Front
    accion: str
    tabla_afectada: str
    id_registro_afectado: int
    detalle_cambio: Optional[Dict[str, Any]]
    fecha_cambio: datetime

    class Config:
        from_attributes = True