"""ASR API Routes"""
from fastapi import APIRouter, File, UploadFile, HTTPException, Form

from app.schemas.asr import ASRResponse, ASRResponseDetail, ASRRequest
from app.services.asr_service import asr_service

router = APIRouter(prefix="/asr", tags=["ASR"])


@router.post("/recognize", response_model=ASRResponseDetail)
async def recognize_audio(
    file: UploadFile = File(..., description="Audio file"),
    detail: bool = Form(False, description="Return detailed information (word-level timestamps)"),
):
    """
    Recognize uploaded audio file

    Supported audio formats: wav, mp3, pcm, opus (ogg container), speex (ogg container), aac, amr

    - **file**: Audio file
    - **detail**: Whether to return detailed information (including word-level timestamps)
    """
    try:
        result = await asr_service.recognize_upload_file(file.file, file.filename)

        if detail:
            return ASRResponseDetail(**result)
        else:
            # Simplified response, only return main information
            return ASRResponseDetail(
                text=result["text"],
                request_id=result["request_id"],
                begin_time=result.get("begin_time", 0),
                end_time=result.get("end_time", 0),
                words=[],
                first_package_delay=result.get("first_package_delay"),
                last_package_delay=result.get("last_package_delay"),
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recognize/path", response_model=ASRResponse)
async def recognize_audio_by_path(request: ASRRequest):
    """
    Recognize audio by file path

    Suitable for audio files already on the server

    - **audio_path**: Audio file path
    - **format**: Audio format (default: wav)
    - **sample_rate**: Sample rate (default: 16000)
    """
    try:
        result = await asr_service.recognize_file(
            file_path=request.audio_path,
            audio_format=request.format,
            sample_rate=request.sample_rate,
        )

        return ASRResponse(
            text=result["text"],
            request_id=result["request_id"],
            begin_time=result.get("begin_time"),
            end_time=result.get("end_time"),
            first_package_delay=result.get("first_package_delay"),
            last_package_delay=result.get("last_package_delay"),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """ASR service health check"""
    try:
        # Try to initialize service to check if configuration is correct
        from app.services.asr_service import ASRService

        ASRService()
        return {"status": "healthy", "service": "bailian-asr"}
    except Exception as e:
        return {"status": "unhealthy", "service": "bailian-asr", "error": str(e)}
