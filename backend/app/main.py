from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings


def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json"
    )
    
    # Настройка CORS
    application.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Базовый эндпоинт для проверки работы
    @application.get("/")
    async def root():
        return {
            "message": "Warehouse Catalog API",
            "version": settings.APP_VERSION,
            "status": "running"
        }
    
    @application.get("/health")
    async def health_check():
        return {"status": "healthy"}
    
    return application


app = create_application()