"""
Schemas para registros de asistencia.
"""

from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Literal


class AttendanceCreate(BaseModel):
    """
    Schema para CREAR un registro de asistencia.

    El Android envía esto al hacer POST /api/v1/attendance/checkin
    """

    uuid: str = Field(..., description="UUID único del registro")
    worker_uuid: str = Field(..., description="UUID del trabajador")
    timestamp: datetime = Field(..., description="Cuándo ocurrió")
    type: Literal["IN", "OUT"] = Field(..., description="Entrada o Salida")
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Confianza del reconocimiento"
    )
    device_id: str = Field(..., description="ID del dispositivo Android")

    @validator("timestamp")
    def timestamp_not_future(cls, v):
        """No permitir registros del futuro"""
        if v > datetime.utcnow():
            raise ValueError("El timestamp no puede ser del futuro")
        return v


class AttendanceResponse(BaseModel):
    """Respuesta con datos de asistencia"""

    id: int
    uuid: str
    worker_id: int
    worker_name: str  # Incluir el nombre para la app
    timestamp: datetime
    type: str
    confidence: float
    device_id: str
    synced_at: datetime

    class Config:
        from_attributes = True


class AttendanceBatchCreate(BaseModel):
    """Para sincronizar múltiples registros a la vez"""

    records: list[AttendanceCreate] = Field(..., max_length=100)  # Máximo 100 por batch
