"""
Configuración central de la aplicación.
Lee variables de entorno y las expone de forma segura.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """
    Configuración de la aplicación.
    Pydantic carga automáticamente las variables del archivo .env
    """

    # Base de datos
    DATABASE_URL: str
    # JWT (autenticación)
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "SIOMA Attendance API"

    class Config:
        env_file = ".env"


# Cache para no leer el .env cada vez
@lru_cache()
def get_settings():
    """Devuelve una instancia única de Settings"""
    return Settings()
