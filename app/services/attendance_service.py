"""
Servicio para operaciones de asistencia.
"""

from sqlalchemy.orm import Session
from app.models.attendance import Attendance
from app.models.worker import Worker
from app.schemas.attendance import AttendanceCreate, AttendanceBatchCreate
from typing import List


class AttendanceService:
    """Servicio para registros de asistencia"""

    @staticmethod
    def create_attendance(db: Session, attendance_data: AttendanceCreate) -> Attendance:
        """
        Crea un registro de asistencia.

        Flow:
        1. Buscar al trabajador por UUID
        2. Verificar que no exista registro duplicado
        3. Crear el registro
        """
        # Buscar trabajador
        worker = (
            db.query(Worker).filter(Worker.uuid == attendance_data.worker_uuid).first()
        )
        if not worker:
            raise ValueError(f"Trabajador no encontrado: {attendance_data.worker_uuid}")

        # Verificar duplicado (mismo UUID de registro)
        existing = (
            db.query(Attendance).filter(Attendance.uuid == attendance_data.uuid).first()
        )
        if existing:
            # Ya existe, no es error (idempotencia para sincronización)
            return existing

        # Crear registro
        db_attendance = Attendance(
            uuid=attendance_data.uuid,
            worker_id=worker.id,
            timestamp=attendance_data.timestamp,
            type=attendance_data.type,
            confidence=attendance_data.confidence,
            device_id=attendance_data.device_id,
        )

        db.add(db_attendance)
        db.commit()
        db.refresh(db_attendance)

        return db_attendance

    @staticmethod
    def create_attendance_batch(db: Session, batch_data: AttendanceBatchCreate) -> dict:
        """
        Crea múltiples registros de asistencia.

        Útil para sincronización offline.
        El Android acumula 50-100 registros y los envía todos juntos.

        Returns:
            {"created": 45, "skipped": 5}
        """
        created_count = 0
        skipped_count = 0
        errors = []

        for attendance_data in batch_data.records:
            try:
                AttendanceService.create_attendance(db, attendance_data)
                created_count += 1
            except ValueError as e:
                # Trabajador no encontrado
                errors.append(str(e))
                skipped_count += 1
            except Exception:
                # Otro error (probablemente duplicado)
                skipped_count += 1

        return {"created": created_count, "skipped": skipped_count, "errors": errors}

    @staticmethod
    def get_worker_attendance(
        db: Session, worker_id: int, limit: int = 50
    ) -> List[Attendance]:
        """Obtiene los últimos N registros de un trabajador"""
        return (
            db.query(Attendance)
            .filter(Attendance.worker_id == worker_id)
            .order_by(Attendance.timestamp.desc())
            .limit(limit)
            .all()
        )
