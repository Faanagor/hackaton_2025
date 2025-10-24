"""
Servicio con la lógica de negocio para trabajadores.

¿Por qué un "Service"?
Separa la lógica de negocio de los endpoints.
Los endpoints solo reciben/devuelven datos.
Los services hacen el trabajo pesado.
"""

from sqlalchemy.orm import Session
from app.models.worker import Worker
from app.schemas.worker import WorkerCreate
from typing import List, Optional
import struct


class WorkerService:
    """Servicio para operaciones de trabajadores"""

    @staticmethod
    def create_worker(db: Session, worker_data: WorkerCreate) -> Worker:
        """
        Crea un nuevo trabajador en la base de datos.

        Args:
            db: Sesión de base de datos
            worker_data: Datos del trabajador (validados por Pydantic)

        Returns:
            Worker creado con su ID asignado
        """
        # Verificar si ya existe un trabajador con ese UUID
        existing = db.query(Worker).filter(Worker.uuid == worker_data.uuid).first()
        if existing:
            raise ValueError(f"Ya existe un trabajador con UUID {worker_data.uuid}")

        # Crear el modelo
        db_worker = Worker(
            uuid=worker_data.uuid,
            name=worker_data.name,
            face_embedding=worker_data.face_embedding,
        )

        # Guardar en BD
        db.add(db_worker)
        db.commit()
        db.refresh(db_worker)  # Para obtener el ID generado

        return db_worker

    @staticmethod
    def get_worker_by_uuid(db: Session, uuid: str) -> Optional[Worker]:
        """Busca un trabajador por UUID"""
        return db.query(Worker).filter(Worker.uuid == uuid).first()

    @staticmethod
    def get_worker_by_id(db: Session, worker_id: int) -> Optional[Worker]:
        """Busca un trabajador por ID"""
        return db.query(Worker).filter(Worker.id == worker_id).first()

    @staticmethod
    def get_all_workers(db: Session, skip: int = 0, limit: int = 100) -> List[Worker]:
        """
        Obtiene lista de trabajadores (paginado).

        Args:
            skip: Cuántos registros saltar (para paginación)
            limit: Máximo de registros a devolver
        """
        return db.query(Worker).offset(skip).limit(limit).all()

    @staticmethod
    def bytes_to_float_array(embedding_bytes: bytes) -> list:
        """
        Convierte bytes a lista de floats.

        Útil para debugging o procesamiento adicional.
        El embedding son 128 floats (128 * 4 bytes = 512 bytes)
        """
        # 'f' = float (4 bytes por número)
        # '<' = little-endian (orden de bytes)
        return list(struct.unpack("<128f", embedding_bytes))
