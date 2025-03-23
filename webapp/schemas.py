"""Schemas module."""

from typing import Optional
from pydantic import BaseModel

"""
Насколько я понял чтобы быть сигмой надо юзать пайдантик 
"""
class TranscriptionBase(BaseModel):
    language: Optional[str] = None


class TranscriptionResponse(BaseModel):
    id: int
    original_filename: str
    language: str | None
    status: str
    text_content: str | None
    result_path: str | None
    user_id: int

    class Config:
        from_attributes = True