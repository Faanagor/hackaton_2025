"""
Aplicación principal FastAPI.
Aquí se configura todo y se registran las rutas.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.db.database import engine, Base
from app.routes import worker_routes, attendance_routes
from app.auth.jwt_handler import create_access_token

settings = get_settings()

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Crear aplicación FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API para sistema de asistencia biométrica offline",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI en http://localhost:8000/docs
    redoc_url="/redoc",  # ReDoc en http://localhost:8000/redoc
)

# Configurar CORS (permitir requests desde Android)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción: especificar IPs/dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar rutas
app.include_router(worker_routes.router, prefix=settings.API_V1_PREFIX)

app.include_router(attendance_routes.router, prefix=settings.API_V1_PREFIX)


# Endpoint raíz
@app.get("/")
async def root():
    """Endpoint de bienvenida"""
    return {"message": "SIOMA Attendance API", "version": "1.0.0", "docs": "/docs"}


# Endpoint para obtener token (solo para testing)
@app.post("/auth/token")
async def get_token(device_id: str):
    """
        Genera un token JWT para un dispositivo.

        En producción, esto debería requerir credenciales.
        Para el MVP, simplificamos.

        **Request:**
    ```
        POST /auth/token
        {
          "device_id": "tablet_001"
        }
    ```

        **Response:**
    ```json
        {
          "access_token": "eyJhbGciOiJIUzI1NiIs...",
          "token_type": "bearer"
        }
    ```

        **Uso desde Android:**
        Guardar este token y enviarlo en headers:
    ```
        Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
    ```
    """
    token = create_access_token(data={"device_id": device_id})
    return {"access_token": token, "token_type": "bearer"}


# Endpoint de health check
@app.get("/health")
async def health_check():
    """Verifica que la API esté funcionando"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    # Correr servidor en desarrollo
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload cuando cambia el código
    )
