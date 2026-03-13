from sqlalchemy import Column, Integer, String, Date, Enum, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class Contrato(Base):
    __tablename__ = "contratos"

    id_contrato = Column(Integer, primary_key=True, index=True, autoincrement=True)
    codigo_unico = Column(String(25), unique=True, nullable=False, index=True)
    
    id_cliente = Column(Integer, ForeignKey("clientes.id_cliente"), nullable=False)
    creado_por = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    
    # TIPOS REALES: Arrendamiento, Suministro, NDA, etc.
    tipo_contrato = Column(String(50), nullable=False) 
    
    # Fechas obligatorias para que el Scheduler funcione
    fecha_inicio = Column(Date, nullable=False)
    fecha_final = Column(Date, nullable=False)
    estado = Column(Enum('vencido', 'activo', 'por_vencer', 'cancelado', 'pendiente'), default='pendiente')
    
    s3_key_contrato = Column(String(255), nullable=True) # El PDF principal

    cliente = relationship("Cliente", back_populates="contratos")
    documentos = relationship("ContratoDocumento", back_populates="contrato", cascade="all, delete-orphan")