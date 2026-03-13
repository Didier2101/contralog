from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.database import Base

class Cargo(Base):
    __tablename__ = "cargos"

    id_cargo = Column(Integer, primary_key=True, index=True, autoincrement=True)
    codigo_cargo = Column(String(15), unique=True, nullable=False, index=True)
    nombre_cargo = Column(String(50), unique=True, nullable=False)
    descripcion = Column(String(255), nullable=True)

    # Relación inversa: Un cargo tiene muchos usuarios
    usuarios = relationship("Usuario", back_populates="cargo")