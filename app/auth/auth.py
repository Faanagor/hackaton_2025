"""
Middleware de autenticación para proteger endpoints.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.auth.jwt_handler import verify_token

# Esquema de seguridad (Bearer Token)
security = HTTPBearer()


async def get_current_device(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Dependencia para validar que el request tenga un token válido.

    Se usa en endpoints protegidos así:
        @router.post("/checkin")
        async def checkin(
            device: dict = Depends(get_current_device)  # <-- Aquí
        ):
            print(f"Dispositivo autenticado: {device['device_id']}")

    Si el token es inválido, lanza HTTPException 401 Unauthorized
    """
    token = credentials.credentials

    try:
        payload = verify_token(token)
        return payload
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
