"""
Endpoints para registros de asistencia.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.schemas.attendance import (
    AttendanceCreate,
    AttendanceResponse,
    AttendanceBatchCreate,
)
from app.services.attendance_service import AttendanceService
from app.auth.auth import get_current_device

router = APIRouter(prefix="/attendance", tags=["attendance"])


@router.post(
    "/checkin",
    response_model=AttendanceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar entrada o salida",
)
async def checkin(
    attendance: AttendanceCreate,
    db: Session = Depends(get_db),
    device: dict = Depends(get_current_device),
):
    """
        Registra una entrada (IN) o salida (OUT) de un trabajador.

        **Flow desde Android:**
        1. Reconoce rostro
        2. Guarda en SQLite local
        3. Cuando hay WiFi: envía a este endpoint

        **Request:**
    ```json
        {
          "uuid": "rec-12345-abcde",
          "worker_uuid": "worker-uuid-here",
          "timestamp": "2025-10-24T08:00:00",
          "type": "IN",
          "confidence": 0.95,
          "device_id": "tablet_001"
        }
    ```
    """
    try:
        db_attendance = AttendanceService.create_attendance(db, attendance)

        # Agregar nombre del trabajador a la respuesta
        response_data = {
            **db_attendance.__dict__,
            "worker_name": db_attendance.worker.name,
        }

        return response_data
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al registrar asistencia: {str(e)}",
        )


@router.post("/sync/batch", summary="Sincronizar múltiples registros")
async def sync_batch(
    batch: AttendanceBatchCreate,
    db: Session = Depends(get_db),
    device: dict = Depends(get_current_device),
):
    """
        Sincroniza múltiples registros de asistencia en una sola petición.

        **Usado para sincronización offline:**
        El Android acumula registros mientras no hay conexión,
        y cuando detecta WiFi los envía todos juntos aquí.

        **Request:**
    ```json
        {
          "records": [
            {
              "uuid": "rec-1",
              "worker_uuid": "worker-1",
              "timestamp": "2025-10-24T08:00:00",
              "type": "IN",
              "confidence": 0.95,
              "device_id": "tablet_001"
            },
            {
              "uuid": "rec-2",
              "worker_uuid": "worker-1",
              "timestamp": "2025-10-24T17:00:00",
              "type": "OUT",
              "confidence": 0.92,
              "device_id": "tablet_001"
            }
          ]
        }
    ```

        **Response:**
    ```json
        {
          "created": 45,
          "skipped": 5,
          "errors": []
        }
    ```
    """
    try:
        result = AttendanceService.create_attendance_batch(db, batch)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en sincronización batch: {str(e)}",
        )


@router.get(
    "/worker/{worker_uuid}",
    response_model=List[AttendanceResponse],
    summary="Historial de asistencia de un trabajador",
)
async def get_worker_attendance(
    worker_uuid: str,
    limit: int = 50,
    db: Session = Depends(get_db),
    device: dict = Depends(get_current_device),
):
    """
    Obtiene el historial de asistencia de un trabajador.

    Útil para ver los últimos registros desde el Android.
    """
    from app.services.worker_service import WorkerService

    # Buscar trabajador
    worker = WorkerService.get_worker_by_uuid(db, worker_uuid)
    if not worker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trabajador no encontrado: {worker_uuid}",
        )

    # Obtener registros
    attendances = AttendanceService.get_worker_attendance(db, worker.id, limit)

    # Agregar nombre del trabajador
    result = []
    for att in attendances:
        result.append({**att.__dict__, "worker_name": worker.name})

    return result
