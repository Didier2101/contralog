from pydantic import BaseModel, Field
from typing import Optional

class CargoBase(BaseModel):
    nombre_cargo: str = Field(..., min_length=2, max_length=50)
    descripcion: Optional[str] = Field(None, max_length=255)

class CargoCreate(CargoBase):
    pass

class CargoUpdate(BaseModel):
    nombre_cargo: Optional[str] = None
    descripcion: Optional[str] = None

class CargoOut(CargoBase):
    id_cargo: int
    codigo_cargo: str

    class Config:
        from_attributes = True