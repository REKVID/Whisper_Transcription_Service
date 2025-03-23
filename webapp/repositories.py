"""Repositories module."""

from contextlib import AbstractAsyncContextManager
from typing import AsyncIterator, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from .models import User, Transcription




class UserRepository:
    def __init__(self, session_factory: AbstractAsyncContextManager[AsyncSession]) -> None:
        self.session_factory = session_factory

    async def get_or_create(self, ip_address: str) -> User:
        async with self.session_factory() as session:
            # ищем
            stmt = select(User).where(User.ip_address == ip_address)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()
            
            if user:
                return user
            
            # Создаем
            user = User(ip_address=ip_address)
            session.add(user)
            try:
                await session.commit()
                await session.refresh(user)
                return user
            except IntegrityError:
                # спиздил
                await session.rollback()
                return await self.get_or_create(ip_address)


"""
полный пиздец, сначла сам писал, 
начал переписавать чтобы все работало асинхронно;
обосрался, но копилот вроде подтер
Надо будет еще разобраться
"""
class TranscriptionRepository:
    def __init__(self, session_factory: AbstractAsyncContextManager[AsyncSession]) -> None:
        self.session_factory = session_factory

    async def _with_session(self, operation):
        # страшная вспомогательная хуйня чтобы убрать дублирование кода
        async with self.session_factory() as session:
            try:
                result = await operation(session)
                return result
            except Exception as e:
                await session.rollback()
                raise

    async def get_all(self) -> AsyncIterator[Transcription]:
        async with self.session_factory() as session:
            result = await session.execute(select(Transcription))
            return result.scalars().all()

    async def get_by_id(self, transcription_id: int) -> Optional[Transcription]:
        async with self.session_factory() as session:
            return await session.get(Transcription, transcription_id)

    async def create(self, file_path: str, 
                    original_filename: str, user_id: int, language: str = None) -> Transcription:
        async def _create(session):
            transcription = Transcription(
                file_path=file_path,
                original_filename=original_filename,
                status="pending",
                language=language,
                user_id=user_id
            )
            session.add(transcription)
            await session.commit()
            await session.refresh(transcription)
            return transcription
            
        return await self._with_session(_create)

    async def update_status(self, transcription_id: int, status: str, 
                          text_content: str = None, result_path: str = None,
                          language: str = None) -> Transcription:
        async def _update(session):
            transcription = await session.get(Transcription, transcription_id)
            
            if not transcription:
                raise ValueError(f"Transcription {transcription_id} not found")
            
            transcription.status = status
        
            updates = {
                'text_content': text_content,
                'result_path': result_path,
                'language': language
            }
            
            for field, value in updates.items():
                if value is not None:
                    setattr(transcription, field, value)
            
            await session.commit()
            await session.refresh(transcription)
            return transcription
                
        return await self._with_session(_update)
