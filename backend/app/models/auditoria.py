from sqlalchemy import Column, Integer, String, JSON, TIMESTAMP, ForeignKey, func
from app.database import Base

class AuditoriaCambio(Base):
    __tablename__ = "auditoria_cambios"

    id_log = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=True)
    accion = Column(String(20), nullable=False) # CREATE, UPDATE, DELETE
    tabla_afectada = Column(String(50), nullable=False)
    id_registro_afectado = Column(Integer, nullable=True)
    detalle_cambio = Column(JSON, nullable=True)
    fecha_cambio = Column(TIMESTAMP, server_default=func.now())