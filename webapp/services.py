"""Services module."""

from typing import AsyncIterator
import asyncio
import aiofiles
import os
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

import logging
from .repositories import UserRepository, TranscriptionRepository
from .models import User, Transcription
from .whisper_service import WhisperService

logger = logging.getLogger(__name__)

# без ограничений все ломается нахуй 
transcription_pool = ThreadPoolExecutor(max_workers=3)
TRANSCRIPTION_SEMAPHORE = asyncio.Semaphore(2) # в ридми написано


class UserService:

    def __init__(self, user_repository: UserRepository) -> None:
        self._repository: UserRepository = user_repository

    async def get_or_create_user(self, ip_address: str) -> User:
        return await self._repository.get_or_create(ip_address)


class TranscriptionService:

    def __init__(self, transcription_repository: TranscriptionRepository,
                 whisper_service: WhisperService) -> None:
        self._repository: TranscriptionRepository = transcription_repository
        self._whisper_service: WhisperService = whisper_service

    async def get_transcriptions(self) -> AsyncIterator[Transcription]:
        return await self._repository.get_all()

    async def get_transcription_by_id(self, transcription_id: int) -> Transcription:
        return await self._repository.get_by_id(transcription_id)

    async def create_transcription(self, file_content: bytes, 
                                 original_filename: str, user_id: int, 
                                 language: str = None) -> Transcription:
        file_path = None
        transcription = None
        
        try:
            os.makedirs("uploads", exist_ok=True)
            
            unique_filename = f"{uuid4()}_{original_filename}"
            file_path = f"uploads/{unique_filename}"
            
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(file_content)
            
            transcription = await self._repository.create(
                file_path=file_path,
                original_filename=original_filename,
                user_id=user_id,
                language=language
            )
            
            # одно из мест где все идет по пизде без ограничения
            async with TRANSCRIPTION_SEMAPHORE:
                result = await asyncio.get_running_loop().run_in_executor(
                    transcription_pool,
                    self._whisper_service.transcribe,
                    file_path
                )
            
            return await self._repository.update_status(
                transcription_id=transcription.id,
                status="completed",
                text_content=result.get("text", ""),
                result_path=result.get("result_path"),
                language=result.get("language", language)
            )
            
        except Exception as e:
            if file_path and os.path.exists(file_path):
                    os.remove(file_path)
                
            if transcription:
                try:
                    await self._repository.update_status(
                        transcription_id=transcription.id,
                        status="failed",
                        text_content=f"Errorr: {str(e)}"
                    )
                except Exception as db_e:
                    logger.error(f"Error updating transcription status: {str(db_e)}")
            
            raise
