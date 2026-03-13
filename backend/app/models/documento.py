
from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, func, Enum, Boolean, Date
from sqlalchemy.orm import relationship
from app.database import Base

class TipoDocumento(Base):
    __tablename__ = "tipo_documentos"
    id_tipo = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)

class ContratoDocumento(Base):
    __tablename__ = "contrato_documentos"

    id_documento = Column(Integer, primary_key=True, autoincrement=True)
    codigo_seguimiento = Column(String(25), unique=True, nullable=False)
    
    # Una sola FK hacia la tabla unificada
    id_contrato = Column(Integer, ForeignKey("contratos.id_contrato", ondelete="CASCADE"), nullable=False)
    id_tipo_doc = Column(Integer, ForeignKey("tipo_documentos.id_tipo"), nullable=False)
    
    s3_key = Column(String(255), nullable=False)
    fecha_subida = Column(TIMESTAMP, server_default=func.now())

    contrato = relationship("Contrato", back_populates="documentos")