"""
Medi-Bridge API Main Entry Point
Medical Consultation Assistant API Service
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router
from app.core.config import settings
from app.core.exceptions import MediBridgeException
from app.schemas.health import HealthResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    # Execute on startup
    print(f"{settings.APP_NAME} v{settings.APP_VERSION} is starting...")
    yield
    # Execute on shutdown
    print(f"{settings.APP_NAME} is shutting down...")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Please restrict to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root route
@app.get("/", response_model=HealthResponse, tags=["Root"])
async def root():
    """Root path health check"""
    return HealthResponse(
        status="ok",
        service=settings.APP_NAME,
        version=settings.APP_VERSION,
        qdrant_connected=True,  # TODO: Actually check connection status
    )


# Register API routes
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


# Global exception handler
@app.exception_handler(MediBridgeException)
async def medi_bridge_exception_handler(request, exc: MediBridgeException):
    """Custom exception handler"""
    from fastapi.responses import JSONResponse

    return JSONResponse(
        status_code=exc.code,
        content={"error": exc.message, "code": exc.code},
    )
