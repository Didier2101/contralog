from sqlalchemy import Column, Integer, ForeignKey, Enum, Float, Date, String, TIMESTAMP, func
from sqlalchemy.orm import relationship
from app.database import Base

class RegistroHora(Base):
    __tablename__ = "registro_horas"

    id_registro = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    id_proyecto = Column(Integer, ForeignKey("proyectos.id_proyecto"), nullable=True) # NULL si es novedad
    
    # Para ausentismos
    tipo_registro = Column(Enum('proyecto', 'novedad'), nullable=False, default='proyecto')
    descripcion_novedad = Column(String(100), nullable=True) # Ej: "Vacaciones", "Incapacidad"
    
    fecha_trabajo = Column(Date, nullable=False)
    cantidad_horas = Column(Float, nullable=False)
    comentario = Column(String(255), nullable=True)
    
    estado_aprobacion = Column(Enum('pendiente', 'aprobado', 'rechazado'), default='pendiente')
    id_aprobador = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=True)
    fecha_aprobacion = Column(TIMESTAMP, nullable=True)

    # Relaciones
    usuario = relationship("Usuario", foreign_keys=[id_usuario])
    proyecto = relationship("Proyecto", back_populates="horas_registradas")
    aprobador = relationship("Usuario", foreign_keys=[id_aprobador])