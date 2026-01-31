"""ASR Related Data Models"""
from pydantic import BaseModel, Field
from typing import Optional


class ASRRequest(BaseModel):
    """ASR request - for file path recognition"""

    audio_path: str = Field(..., description="Audio file path")
    format: Optional[str] = Field(default="wav", description="Audio format")
    sample_rate: Optional[int] = Field(default=16000, description="Sample rate")


class ASRResponse(BaseModel):
    """ASR response"""

    text: str = Field(..., description="Recognition result text")
    request_id: str = Field(..., description="Request ID")
    begin_time: Optional[int] = Field(None, description="Begin time (ms)")
    end_time: Optional[int] = Field(None, description="End time (ms)")
    first_package_delay: Optional[float] = Field(None, description="First package delay (ms)")
    last_package_delay: Optional[float] = Field(None, description="Last package delay (ms)")


class WordTimestamp(BaseModel):
    """Word timestamp"""

    text: str = Field(..., description="Word")
    begin_time: int = Field(..., description="Begin time (ms)")
    end_time: int = Field(..., description="End time (ms)")
    punctuation: Optional[str] = Field(None, description="Punctuation")


class ASRResponseDetail(BaseModel):
    """ASR detailed response (with timestamps)"""

    text: str = Field(..., description="Recognition result text")
    request_id: str = Field(..., description="Request ID")
    begin_time: int = Field(..., description="Begin time (ms)")
    end_time: int = Field(..., description="End time (ms)")
    words: list[WordTimestamp] = Field(default_factory=list, description="Word timestamp list")
    first_package_delay: Optional[float] = Field(None, description="First package delay (ms)")
    last_package_delay: Optional[float] = Field(None, description="Last package delay (ms)")
