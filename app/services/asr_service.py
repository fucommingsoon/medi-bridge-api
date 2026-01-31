"""Bailian ASR Service"""
import os
import tempfile
from pathlib import Path
from typing import BinaryIO

import dashscope
from dashscope.audio.asr import Recognition
from http import HTTPStatus

from app.core.config import settings
from app.core.exceptions import ASRServiceError, InvalidAudioFileError


class ASRService:
    """Bailian ASR service"""

    def __init__(self):
        self._initialized = False

    def _ensure_initialized(self):
        """Ensure API Key is configured"""
        if self._initialized:
            return

        # Set API Key
        if settings.BAILIAN_API_KEY:
            dashscope.api_key = settings.BAILIAN_API_KEY
        else:
            # Try to get from environment variable BAILIAN_API_KEY
            api_key = os.environ.get("BAILIAN_API_KEY")
            if not api_key:
                raise ASRServiceError("BAILIAN_API_KEY not configured")
            dashscope.api_key = api_key

        self._initialized = True

    async def recognize_file(
        self,
        file_path: str,
        audio_format: str | None = None,
        sample_rate: int | None = None,
    ) -> dict:
        """
        Recognize local audio file

        Args:
            file_path: Audio file path
            audio_format: Audio format (wav, mp3, pcm, opus, speex, aac, amr)
            sample_rate: Sample rate, default 16000

        Returns:
            Recognition result
        """
        self._ensure_initialized()
        audio_format = audio_format or settings.FUN_ASR_FORMAT
        sample_rate = sample_rate or settings.FUN_ASR_SAMPLE_RATE

        # Check if file exists
        if not Path(file_path).exists():
            raise InvalidAudioFileError(f"File not found: {file_path}")

        # Check file size
        file_size = Path(file_path).stat().st_size
        if file_size == 0:
            raise InvalidAudioFileError("Audio file is empty")

        try:
            # Create Recognition instance
            recognition = Recognition(
                model=settings.FUN_ASR_MODEL,
                format=audio_format,
                sample_rate=sample_rate,
                callback=None,
            )

            # Synchronous recognition call
            result = recognition.call(file_path)

            if result.status_code != HTTPStatus.OK:
                raise ASRServiceError(
                    f"Speech recognition failed: {result.message} (code: {result.status_code})"
                )

            # Get recognition result
            sentences = result.get_sentence()

            # get_sentence() returns a list, take the first sentence
            if not sentences or len(sentences) == 0:
                raise ASRServiceError("Speech recognition returned no results")

            sentence = sentences[0]

            return {
                "text": sentence.get("text", ""),
                "request_id": result.get_request_id(),
                "begin_time": sentence.get("begin_time"),
                "end_time": sentence.get("end_time"),
                "words": [
                    {
                        "text": w.get("text"),
                        "begin_time": w.get("begin_time"),
                        "end_time": w.get("end_time"),
                        "punctuation": w.get("punctuation"),
                    }
                    for w in sentence.get("words", [])
                ] if sentence.get("words") else [],
                "first_package_delay": recognition.get_first_package_delay(),
                "last_package_delay": recognition.get_last_package_delay(),
            }

        except InvalidAudioFileError:
            raise
        except ASRServiceError:
            raise
        except Exception as e:
            raise ASRServiceError(f"Speech recognition error: {str(e)}")

    async def recognize_bytes(
        self,
        audio_data: bytes,
        audio_format: str = "wav",
        filename: str = "audio",
    ) -> dict:
        """
        Recognize binary audio data

        Args:
            audio_data: Audio binary data
            audio_format: Audio format
            filename: Filename (for generating temporary file)

        Returns:
            Recognition result
        """
        if not audio_data:
            raise InvalidAudioFileError("Audio data is empty")

        # Create temporary file
        with tempfile.NamedTemporaryFile(
            suffix=f".{audio_format}", delete=False
        ) as temp_file:
            temp_file.write(audio_data)
            temp_file_path = temp_file.name

        try:
            return await self.recognize_file(temp_file_path, audio_format)
        finally:
            # Clean up temporary file
            Path(temp_file_path).unlink(missing_ok=True)

    async def recognize_upload_file(
        self,
        file: BinaryIO,
        filename: str,
    ) -> dict:
        """
        Recognize uploaded audio file

        Args:
            file: Uploaded file object
            filename: Filename

        Returns:
            Recognition result
        """
        # Determine format based on filename
        audio_format = self._get_audio_format(filename)

        # Read file content
        audio_data = file.read()

        return await self.recognize_bytes(audio_data, audio_format, filename)

    @staticmethod
    def _get_audio_format(filename: str) -> str:
        """Get audio format based on filename"""
        ext = Path(filename).suffix.lower().lstrip(".")
        supported_formats = ["pcm", "wav", "mp3", "opus", "speex", "aac", "amr", "ogg"]
        if ext not in supported_formats:
            # opus/speex use ogg container
            if ext == "ogg":
                return "opus"
            raise InvalidAudioFileError(
                f"Unsupported audio format: {ext}, supported formats: {', '.join(supported_formats)}"
            )
        return ext


# Global service instance (lazy initialization)
asr_service = ASRService()
