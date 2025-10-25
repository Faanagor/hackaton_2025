"""
Modelo de base de datos para trabajadores.
Representa la tabla 'workers' en PostgreSQL.
"""

from sqlalchemy import Column, Integer, String, LargeBinary, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.database import Base


class Worker(Base):
    """
    Tabla de trabajadores.

    Campos:
    - id: Identificador único
    - uuid: UUID para sincronización entre dispositivos
    - name: Nombre del trabajador
    - face_embedding: Vector del rostro (128 floats guardados como bytes)
    - created_at: Cuándo se registró
    - updated_at: Última actualización
    """

    __tablename__ = "workers"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    face_embedding = Column(LargeBinary, nullable=False)

    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )

    # Relación con attendance (un trabajador tiene muchas asistencias)
    # attendances = relationship("Attendance", back_populates="worker")
    attendances = relationship(
        "Attendance",
        back_populates="worker",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self):
        return f"<Worker(id={self.id}, name='{self.name}')>"
