"""
Schemas Pydantic para validación de datos de trabajadores.

¿Qué hace Pydantic?
- Valida que los datos recibidos sean correctos
- Convierte tipos automáticamente
- Genera documentación automática en Swagger
"""

from pydantic import BaseModel, Field, field_validator
from datetime import datetime


class WorkerBase(BaseModel):
    """Campos comunes de un trabajador"""

    name: str = Field(..., min_length=3, max_length=100)


class WorkerCreate(WorkerBase):
    """
    Schema para CREAR un trabajador.

    Lo que el Android envía al hacer POST /api/v1/workers/register
    """

    uuid: str = Field(..., description="UUID generado por el dispositivo")
    face_embedding: bytes = Field(..., description="Embedding del rostro (128 floats)")

    @field_validator("name")
    def name_must_not_be_empty(cls, v):
        """Valida que el nombre no esté vacío"""
        if not v or not v.strip():
            raise ValueError("El nombre no puede estar vacío")
        return v.strip().title()  # "juan perez" -> "Juan Perez"


class WorkerResponse(WorkerBase):
    """
    Schema para RESPONDER con datos de un trabajador.

    Lo que la API devuelve al Android.
    """

    id: int
    uuid: str
    created_at: datetime
    updated_at: datetime

    class Config:
        # Permite crear desde un modelo SQLAlchemy
        from_attributes = True


class WorkerListResponse(BaseModel):
    """Lista de trabajadores (sin embeddings por performance)"""

    id: int
    uuid: str
    name: str
    created_at: datetime

    class Config:
        from_attributes = True
