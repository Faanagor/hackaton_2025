"""
Schemas para registros de asistencia.
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime, timezone
from typing import Literal, Optional
import uuid as uuid_lib


class AttendanceCreate(BaseModel):
    """
    Schema para CREAR un registro de asistencia.
    El Android envía esto al hacer POST /api/v1/attendance/checkin
    """

    worker_uuid: str = Field(..., description="UUID del trabajador")
    type: Literal["IN", "OUT"] = Field(..., description="Entrada o Salida")
    uuid: str = Field(
        default_factory=lambda: str(uuid_lib.uuid4()),
        description="UUID único del registro",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Cuándo ocurrió (UTC)",
    )
    confidence: Optional[float] = Field(
        default=1.0, ge=0.0, le=1.0, description="Confianza del reconocimiento facial"
    )
    device_id: Optional[str] = Field(
        default="unknown",
        description="ID del dispositivo Android que envía el registro",
    )

    @field_validator("timestamp")
    @classmethod
    def timestamp_not_future(cls, v: datetime) -> datetime:
        """No permitir registros con timestamp futuro"""
        now_utc = datetime.now(timezone.utc)
        if v.tzinfo is None or v.tzinfo.utcoffset(v) is None:
            # Si no tiene tz, asumir UTC
            v = v.replace(tzinfo=timezone.utc)
        if v > now_utc:
            raise ValueError("El timestamp no puede ser del futuro")
        return v

    # 🔹 Ejemplo para Swagger UI
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "worker_uuid": "abc-123-def-456",
                "type": "IN",
                "confidence": 0.95,
                "device_id": "tablet_001",
            }
        }
    )


class AttendanceResponse(BaseModel):
    """Respuesta con datos de asistencia"""

    id: int
    uuid: str
    worker_id: int
    worker_name: str
    timestamp: datetime
    type: str
    confidence: Optional[float]
    device_id: Optional[str]
    synced_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class AttendanceBatchCreate(BaseModel):
    """Para sincronizar múltiples registros a la vez"""

    records: list[AttendanceCreate] = Field(
        ..., min_length=1, max_length=100, description="Lista de registros (máximo 100)"
    )


class AttendanceBatchResponse(BaseModel):
    """Respuesta de sincronización por lotes"""

    success: int = Field(
        ..., description="Cantidad de registros procesados exitosamente"
    )
    failed: int = Field(default=0, description="Cantidad de registros fallidos")
    errors: Optional[list[str]] = Field(
        default=None, description="Mensajes de error si los hay"
    )


# """
# Schemas para registros de asistencia.
# """
# from pydantic import BaseModel, Field, field_validator
# from datetime import datetime, timezone
# from typing import Literal, Optional
# import uuid as uuid_lib

# class AttendanceCreate(BaseModel):
#     """
#     Schema para CREAR un registro de asistencia.
#     El Android envía esto al hacer POST /api/v1/attendance/checkin
#     """
#     uuid: str = Field(
#         default_factory=lambda: str(uuid_lib.uuid4()),
#         description="UUID único del registro"
#     )
#     worker_uuid: str = Field(..., description="UUID del trabajador")
#     timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Cuándo ocurrió")
#     type: Literal["IN", "OUT"] = Field(..., description="Entrada o Salida")
#     confidence: Optional[float] = Field(
#         default=1.0,
#         ge=0.0,
#         le=1.0,
#         description="Confianza del reconocimiento"
#     )
#     device_id: Optional[str] = Field(
#         default="unknown",
#         description="ID del dispositivo Android"
#     )

#     @field_validator("timestamp")
#     @classmethod
#     def timestamp_not_future(cls, v: datetime) -> datetime:
#         """No permitir registros del futuro"""
#         if v > datetime.utcnow():
#             raise ValueError("El timestamp no puede ser del futuro")
#         return v

#     class Config:
#         json_schema_extra = {
#             "example": {
#                 "worker_uuid": "abc-123-def-456",
#                 "type": "IN",
#                 "confidence": 0.95,
#                 "device_id": "tablet_001"
#             }
#         }


# class AttendanceResponse(BaseModel):
#     """Respuesta con datos de asistencia"""
#     id: int
#     uuid: str
#     worker_id: int
#     worker_name: str  # Incluir el nombre para la app
#     timestamp: datetime
#     type: str
#     confidence: Optional[float]
#     device_id: Optional[str]
#     synced_at: datetime

#     class Config:
#         from_attributes = True


# class AttendanceBatchCreate(BaseModel):
#     """Para sincronizar múltiples registros a la vez"""
#     records: list[AttendanceCreate] = Field(
#         ...,
#         min_length=1,
#         max_length=100,
#         description="Lista de registros (máximo 100)"
#     )


# class AttendanceBatchResponse(BaseModel):
#     """Respuesta de sincronización por lotes"""
#     success: int = Field(..., description="Cantidad de registros procesados exitosamente")
#     failed: int = Field(default=0, description="Cantidad de registros fallidos")
#     errors: Optional[list[str]] = Field(default=None, description="Mensajes de error si los hay")
