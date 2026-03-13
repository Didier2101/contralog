from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class RegistroHoraBase(BaseModel):
    id_proyecto: Optional[int] = None
    tipo_registro: str = Field(..., pattern="^(proyecto|novedad)$")
    descripcion_novedad: Optional[str] = None # Vacaciones, Incapacidad, etc.
    fecha_trabajo: date
    cantidad_horas: float = Field(..., gt=0, le=24)
    comentario: Optional[str] = None

class RegistroHoraCreate(RegistroHoraBase):
    pass

class RegistroHoraOut(RegistroHoraBase):
    id_registro: int
    id_usuario: int
    estado_aprobacion: str
    
    class Config:
        from_attributes = True