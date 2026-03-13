from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Float, Date, DECIMAL
from sqlalchemy.orm import relationship
from app.database import Base

class Proyecto(Base):
    __tablename__ = "proyectos"

    id_proyecto = Column(Integer, primary_key=True, index=True)
    id_cliente = Column(Integer, ForeignKey("clientes.id_cliente"), nullable=False)
    id_contrato = Column(Integer, ForeignKey("contratos.id_contrato"), nullable=True)
    
    nombre_proyecto = Column(String(150), nullable=False)
    
    # Basado exactamente en tus imágenes de Pipeline
    etapa = Column(Enum(
        'prospeccion', 'contacto', 'propuesta', 'negociacion', 'ejecucion', 'finalizado'
    ), default='prospeccion')
    
    horas_estimadas = Column(Float, default=0.0)
    presupuesto_inicial = Column(DECIMAL(15, 2), default=0.0)
    fecha_inicio = Column(Date, nullable=True)

    # Relaciones
    cliente = relationship("Cliente", back_populates="proyectos")
    contrato = relationship("Contrato")
    horas_registradas = relationship("RegistroHora", back_populates="proyecto")