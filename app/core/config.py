"""Application Configuration"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration class"""

    # Application basic information
    APP_NAME: str = "Medi-Bridge API"
    APP_VERSION: str = "0.1.0"
    APP_DESCRIPTION: str = "Medical Consultation Assistant API Service"
    DEBUG: bool = False

    # API configuration
    API_V1_PREFIX: str = "/api/v1"

    # Qdrant vector database configuration
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION_NAME: str = "medical_knowledge"
    QDRANT_API_KEY: str | None = None

    # Vector search configuration
    VECTOR_SIZE: int = 1024  # text-embedding-v4 output dimension
    TOP_K_RESULTS: int = 5
    SIMILARITY_THRESHOLD: float = 0.7

    # Bailian ASR configuration
    BAILIAN_API_KEY: str = ""
    FUN_ASR_MODEL: str = "fun-asr-realtime"
    FUN_ASR_SAMPLE_RATE: int = 16000
    FUN_ASR_FORMAT: str = "wav"  # Supported formats: pcm, wav, mp3, opus, speex, aac, amr

    # Bailian Embedding configuration
    EMBEDDING_MODEL: str = "text-embedding-v4"
    EMBEDDING_DIMENSION: int = 1024  # text-embedding-v4 output dimension

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
