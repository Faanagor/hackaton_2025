"""
Endpoints (rutas) para operaciones de trabajadores.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.schemas.worker import WorkerCreate, WorkerResponse, WorkerListResponse
from app.services.worker_service import WorkerService
from app.auth.auth import get_current_device

# Crear router
router = APIRouter(
    prefix="/workers",
    tags=["workers"],  # Para agrupar en la documentación
)


@router.post(
    "/register",
    response_model=WorkerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo trabajador",
)
async def register_worker(
    worker: WorkerCreate,
    db: Session = Depends(get_db),
    device: dict = Depends(get_current_device),  # Requiere autenticación
):
    """
        Registra un nuevo trabajador en el sistema.

        **Flow desde Android:**
        1. Usuario captura 5-10 fotos
        2. Android extrae embedding promedio
        3. Android hace POST a este endpoint
        4. Backend guarda en PostgreSQL

        **Request:**
    ```json
        {
          "uuid": "550e8400-e29b-41d4-a716-446655440000",
          "name": "Juan Pérez",
          "face_embedding": "<bytes del embedding>"
        }
    ```

        **Response:**
    ```json
        {
          "id": 1,
          "uuid": "550e8400-e29b-41d4-a716-446655440000",
          "name": "Juan Pérez",
          "created_at": "2025-10-24T10:30:00",
          "updated_at": "2025-10-24T10:30:00"
        }
    ```
    """
    try:
        db_worker = WorkerService.create_worker(db, worker)
        return db_worker
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear trabajador: {str(e)}",
        )


@router.get(
    "/list",
    response_model=List[WorkerListResponse],
    summary="Listar todos los trabajadores",
)
async def list_workers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    device: dict = Depends(get_current_device),
):
    """
    Lista todos los trabajadores registrados (sin embeddings).

    Usado por el Android para mostrar lista de trabajadores.
    """
    workers = WorkerService.get_all_workers(db, skip, limit)
    return workers


@router.get(
    "/{worker_uuid}",
    response_model=WorkerResponse,
    summary="Obtener un trabajador por UUID",
)
async def get_worker(
    worker_uuid: str,
    db: Session = Depends(get_db),
    device: dict = Depends(get_current_device),
):
    """Obtiene los datos de un trabajador específico"""
    worker = WorkerService.get_worker_by_uuid(db, worker_uuid)

    if not worker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trabajador no encontrado: {worker_uuid}",
        )

    return worker
