"""Custom Exception Classes"""


class MediBridgeException(Exception):
    """Base exception class"""

    def __init__(self, message: str, code: int = 500):
        self.message = message
        self.code = code
        super().__init__(self.message)


class VectorSearchError(MediBridgeException):
    """Vector search exception"""

    def __init__(self, message: str = "Vector search failed"):
        super().__init__(message, code=500)


class QdrantConnectionError(MediBridgeException):
    """Qdrant connection exception"""

    def __init__(self, message: str = "Unable to connect to vector database"):
        super().__init__(message, code=503)


class InvalidQueryError(MediBridgeException):
    """Invalid query exception"""

    def __init__(self, message: str = "Invalid query content"):
        super().__init__(message, code=400)


class ASRServiceError(MediBridgeException):
    """ASR service exception"""

    def __init__(self, message: str = "Speech recognition failed"):
        super().__init__(message, code=500)


class InvalidAudioFileError(MediBridgeException):
    """Invalid audio file exception"""

    def __init__(self, message: str = "Invalid audio file or unsupported format"):
        super().__init__(message, code=400)


class SQLiteServiceError(MediBridgeException):
    """SQLite service exception"""

    def __init__(self, message: str = "SQLite service operation failed"):
        super().__init__(message, code=500)


class SQLiteConnectionError(MediBridgeException):
    """SQLite connection exception"""

    def __init__(self, message: str = "Unable to connect to SQLite database"):
        super().__init__(message, code=503)
