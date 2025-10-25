from datetime import datetime, timezone
from enum import Enum as PyEnum
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Index,
    Enum,
)
from sqlalchemy.orm import relationship
from app.db.database import Base


class AttendanceType(PyEnum):
    IN = "IN"
    OUT = "OUT"


class Attendance(Base):
    __tablename__ = "attendance"

    # 🔑 Clave primaria autoincremental
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    uuid = Column(String, unique=True, nullable=False)
    # 👷 Relación con el trabajador
    worker_id = Column(
        Integer, ForeignKey("workers.id", ondelete="CASCADE"), nullable=False
    )
    worker = relationship("Worker", back_populates="attendances")
    # 🕒 Información del registro
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    type = Column(Enum(AttendanceType, name="attendance_type_enum"), nullable=False)
    confidence = Column(Float, nullable=True)
    device_id = Column(String, nullable=True)
    # 🔄 Sincronización
    synced_at = Column(DateTime(timezone=True), nullable=True)
    # 🧾 Auditoría
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # ⚡ Índices compuestos para acelerar consultas
    __table_args__ = (
        Index("ix_attendance_worker_timestamp", "worker_id", "timestamp"),
    )

    def __repr__(self):
        return (
            f"<Attendance(id={self.id}, worker_id={self.worker_id}, "
            f"type={self.type.value}, timestamp={self.timestamp}, confidence={self.confidence})>"
        )


# """
# Modelo de base de datos para registros de asistencia.
# """

# from sqlalchemy import (
#     Column,
#     Integer,
#     String,
#     DateTime,
#     Float,
#     ForeignKey,
#     Enum as SqlEnum,
# )
# from sqlalchemy.dialects.postgresql import UUID as PgUUID
# from sqlalchemy.orm import relationship, declarative_base
# from datetime import datetime, timezone
# from enum import Enum
# import uuid

# from app.db.database import Base


# class AttendanceType(str, Enum):
#     """Tipo de registro de asistencia"""
#     IN = "IN"
#     OUT = "OUT"


# class Attendance(Base):
#     """
#     Tabla de registros de asistencia (entradas/salidas).

#     Representa cada vez que un trabajador marca entrada o salida
#     desde un dispositivo móvil (tablet o teléfono).
#     """

#     __tablename__ = "attendance_records"

#     id = Column(Integer, primary_key=True, index=True)
#     # Usamos UUID nativo (seguridad + unicidad)
#     uuid = Column(PgUUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4, index=True)
#     # Relación con el trabajador
#     worker_id = Column(Integer, ForeignKey("workers.id", ondelete="CASCADE"), nullable=False)
#     # Hora del registro (con timezone obligatorio)
#     timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
#     type = Column(SqlEnum(AttendanceType), nullable=False) # Entrada o salida
#     confidence = Column(Float, nullable=False) # Confianza del reconocimiento facial (0.0 a 1.0)
#     device_id = Column(String, nullable=False) # Dispositivo Android usado
#     # Cuándo se sincronizó con el servidor
#     synced_at = Column(
#         DateTime(timezone=True),
#         default=lambda: datetime.now(timezone.utc),
#         nullable=False,
#     )
#     # Auditoría
#     created_at = Column(
#         DateTime(timezone=True),
#         default=lambda: datetime.now(timezone.utc),
#         nullable=False,
#     )
#     updated_at = Column(
#         DateTime(timezone=True),
#         default=lambda: datetime.now(timezone.utc),
#         onupdate=lambda: datetime.now(timezone.utc),
#         nullable=False,
#     )
#     # Relación inversa
#     worker = relationship(
#         "Worker",
#         back_populates="attendances",
#         lazy="joined",
#     )


#     def __repr__(self):
#         return (
#             f"<Attendance(id={self.id}, worker_id={self.worker_id}, "
#             f"type='{self.type}', timestamp={self.timestamp.isoformat()})>"
#         )

#################################################################

# """
# Modelo de base de datos para registros de asistencia.
# """

# from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
# from sqlalchemy.orm import relationship
# from datetime import datetime, timezone
# from app.db.database import Base


# class Attendance(Base):
#     """
#     Tabla de registros de asistencia (entradas/salidas).

#     Campos:
#     - id: Identificador único
#     - uuid: UUID del registro (para sincronización)
#     - worker_id: Referencia al trabajador
#     - timestamp: Cuándo ocurrió el registro
#     - type: 'IN' (entrada) o 'OUT' (salida)
#     - confidence: Qué tan seguro estaba el reconocimiento (0.0 - 1.0)
#     - device_id: Qué tablet/celular registró esto
#     """

#     __tablename__ = "attendance_records"

#     id = Column(Integer, primary_key=True, index=True)
#     uuid = Column(String, unique=True, index=True, nullable=False)

#     # Foreign key al trabajador
#     worker_id = Column(Integer, ForeignKey("workers.id"), nullable=False)

#     timestamp = Column(DateTime, nullable=False, index=True)
#     type = Column(String, nullable=False)  # 'IN' o 'OUT'
#     confidence = Column(Float)  # 0.0 - 1.0
#     device_id = Column(String)  # Identificador del dispositivo Android

#     synced_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

#     # Relación inversa
#     worker = relationship("Worker", back_populates="attendances")

#     def __repr__(self):
#         return f"<Attendance(worker_id={self.worker_id}, type='{self.type}', timestamp={self.timestamp})>"
