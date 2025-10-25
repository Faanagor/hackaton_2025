"""
Manejo de JWT (JSON Web Tokens) para autenticación.

¿Qué es JWT?
Un "token" que identifica al dispositivo Android.
Como una "tarjeta de acceso" que expira después de un tiempo.
"""

from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from jose import JWTError, jwt
from app.core.config import get_settings


settings = get_settings()


def create_access_token(data: dict) -> str:
    """
    Crea un token JWT.
    Args:
        data: Datos a incluir en el token (ej: {"device_id": "tablet_001"})
    Returns:
        String con el token JWT
    Ejemplo de uso:
        token = create_access_token({"device_id": "tablet_001"})
        # Devuelve: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    """
    to_encode = data.copy()
    # El token expira en 15 minutos (configurado en .env)

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    # Crear el token
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str) -> dict:
    """
    Verifica y decodifica un token JWT.
    Args:
        token: Token JWT recibido del Android
    Returns:
        Diccionario con los datos del token
    Raises:
        JWTError: Si el token es inválido o expiró
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            # options={"verify_exp": True},
            # leeway=60  # permite hasta 60 seg de diferencia de reloj
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
        )
