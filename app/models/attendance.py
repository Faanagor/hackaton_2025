"""
Modelo de base de datos para registros de asistencia.
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class Attendance(Base):
    """
    Tabla de registros de asistencia (entradas/salidas).

    Campos:
    - id: Identificador único
    - uuid: UUID del registro (para sincronización)
    - worker_id: Referencia al trabajador
    - timestamp: Cuándo ocurrió el registro
    - type: 'IN' (entrada) o 'OUT' (salida)
    - confidence: Qué tan seguro estaba el reconocimiento (0.0 - 1.0)
    - device_id: Qué tablet/celular registró esto
    """

    __tablename__ = "attendance_records"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, unique=True, index=True, nullable=False)

    # Foreign key al trabajador
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=False)

    timestamp = Column(DateTime, nullable=False, index=True)
    type = Column(String, nullable=False)  # 'IN' o 'OUT'
    confidence = Column(Float)  # 0.0 - 1.0
    device_id = Column(String)  # Identificador del dispositivo Android

    synced_at = Column(DateTime, default=datetime.utcnow)

    # Relación inversa
    worker = relationship("Worker", back_populates="attendances")

    def __repr__(self):
        return f"<Attendance(worker_id={self.worker_id}, type='{self.type}', timestamp={self.timestamp})>"
