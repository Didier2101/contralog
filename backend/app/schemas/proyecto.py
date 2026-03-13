from pydantic import BaseModel
from typing import Optional
from datetime import date
from decimal import Decimal

class ProyectoBase(BaseModel):
    nombre_proyecto: str
    id_cliente: int
    etapa: Optional[str] = "prospeccion"
    horas_estimadas: Optional[float] = 0.0
    presupuesto_inicial: Optional[Decimal] = 0.0

class ProyectoCreate(ProyectoBase):
    pass

class ProyectoUpdate(BaseModel):
    nombre_proyecto: Optional[str] = None
    etapa: Optional[str] = None
    id_contrato: Optional[int] = None
    fecha_inicio: Optional[date] = None

class ProyectoOut(ProyectoBase):
    id_proyecto: int
    id_contrato: Optional[int] = None
    
    class Config:
        from_attributes = True