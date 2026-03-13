from sqlalchemy import Column, Integer, String, Enum, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import relationship
# Importamos Base desde el nuevo database.py que configuramos
from app.database import Base 

class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario = Column(Integer, primary_key=True, index=True, autoincrement=True)
    codigo_usuario = Column(String(25), unique=True, nullable=False, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    
    # IMPORTANTE: Los Enums aquí deben ser idénticos a los de la DB
    rol = Column(Enum('admin', 'aprobador', 'funcionario', name='rol_usuario'), nullable=False)
    estado = Column(Enum('activo', 'inactivo', name='estado_usuario'), default='activo')
    
    id_cargo = Column(Integer, ForeignKey("cargos.id_cargo", ondelete="SET NULL"), nullable=True)
    
    ultimo_ingreso = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relación con la tabla de cargos
    # Usamos string "Cargo" para evitar errores si el modelo Cargo se define después
    cargo = relationship("Cargo", back_populates="usuarios")