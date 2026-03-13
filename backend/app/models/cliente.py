from sqlalchemy import Column, Integer, String, Enum, TIMESTAMP, func
from sqlalchemy.orm import relationship
from app.database import Base

class Cliente(Base):
    __tablename__ = "clientes"

    id_cliente = Column(Integer, primary_key=True, index=True, autoincrement=True)
    codigo_cliente = Column(String(20), unique=True, nullable=False, index=True)
    
    tipo_persona = Column(Enum('natural', 'juridica', name='tipo_persona'), nullable=False)
    tipo_identificacion = Column(Enum('NIT', 'CC', 'CE', 'RUT', name='tipo_doc'), nullable=False)
    
    identificacion_fiscal = Column(String(20), unique=True, nullable=False, index=True)
    nombre_razon_social = Column(String(150), nullable=False, index=True)
    
    email_contacto = Column(String(150), nullable=True)
    telefono = Column(String(25), nullable=True)
    direccion = Column(String(255), nullable=True)
    
    estado = Column(Enum('activo', 'inactivo', name='estado_cliente'), default='activo')
    created_at = Column(TIMESTAMP, server_default=func.now())

    # --- RELACIONES (EL CORAZÓN DEL ERROR) ---
    # Faltaba esta línea. El nombre "contratos" debe coincidir con el back_populates de Contrato
    contratos = relationship("Contrato", back_populates="cliente") 
    proyectos = relationship("Proyecto", back_populates="cliente")