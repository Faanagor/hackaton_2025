"""
Conexión a la base de datos PostgreSQL usando SQLAlchemy.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import get_settings

settings = get_settings()

# Motor de base de datos
# echo=True muestra las queries SQL en consola (útil para debug)
engine = create_engine(
    settings.DATABASE_URL,
    echo=True,  # Cambiar a False en producción
    pool_size=5,  # Número de conexiones en el pool
    max_overflow=10,
)

# Fábrica de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Clase base para los modelos
Base = declarative_base()


def get_db():
    """
    Dependencia para obtener una sesión de base de datos.

    Se usa en los endpoints así:
        def mi_endpoint(db: Session = Depends(get_db)):
            ...

    Automáticamente cierra la conexión al terminar.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
