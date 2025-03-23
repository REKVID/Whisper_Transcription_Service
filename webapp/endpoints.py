"""Endpoints module."""

from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, Request
from dependency_injector.wiring import inject, Provide

from .containers import Container
from .services import TranscriptionService, UserService
from .schemas import TranscriptionResponse

router = APIRouter()


# получение всех транскрипций
@router.get("/transcriptions", response_model=List[TranscriptionResponse])
@inject
async def get_transcriptions(
    transcription_service: TranscriptionService = Depends(Provide[Container.transcription_service]),
) -> List[TranscriptionResponse]:
    return list(await transcription_service.get_transcriptions())


# получение транскрипции по id
@router.get("/transcriptions/{transcription_id}", response_model=TranscriptionResponse)
@inject
async def get_transcription(
    transcription_id: int,
    transcription_service: TranscriptionService = Depends(Provide[Container.transcription_service]),
) -> TranscriptionResponse:
    return await transcription_service.get_transcription_by_id(transcription_id)


# создание транскрипции
@router.post("/transcriptions", response_model=TranscriptionResponse)
@inject
async def create_transcription(
    request: Request,
    language: str = None,
    file: UploadFile = File(...),
    transcription_service: TranscriptionService = Depends(Provide[Container.transcription_service]),
    user_service: UserService = Depends(Provide[Container.user_service]),
) -> TranscriptionResponse:
    try:
        content = await file.read()
    
        """ 2 строчки можно убрать и оставить только request.client.host
        но это мне нужно было для того чтобы убедется,
        что можно отправлять несколько запросов на обработку одновременно(в ридми написано)
        """
        forwarded_for = request.headers.get("X-Forwarded-For")
        client_ip = forwarded_for.split(",")[0].strip() if forwarded_for else request.client.host
        
        user = await user_service.get_or_create_user(client_ip)
        
        transcription = await transcription_service.create_transcription(
            file_content=content,
            original_filename=file.filename,
            user_id=user.id,
            language=language
        )
        
        return transcription
        
    except Exception as e:
        raise
