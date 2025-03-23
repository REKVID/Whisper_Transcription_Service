"""Whisper service module."""

import json
import os
import whisper
import logging
from typing import Dict, Any
import threading

logger = logging.getLogger(__name__)

# логировал все чтобы найти проблему (нашел)
class WhisperService:

    def __init__(self):
        # инициализирует и блокирует от нескольких потоков (в ридми написано)
        self.model = whisper.load_model("tiny")
        self.model_lock = threading.RLock()
        logger.info("Whisper model loaded")

    def transcribe(self, file_path: str) -> Dict[str, Any]:
        try:
            logger.info(f"Starting transcription of {file_path}")
            
            with self.model_lock:
                result = self.model.transcribe(file_path)
                logger.info(f"Transcription completed for {file_path}")
            
            os.makedirs("results", exist_ok=True)
            
            result_path = f"results/{os.path.basename(file_path)}.json"
            with open(result_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Transcription results saved to {result_path}")
            
            return {
                "text": result["text"],
                "language": result["language"],
                "result_path": result_path
            }
            
        except Exception as e:
            logger.error(f"Erroer transcribing file:  {str(e)}")
            return {
                "text": "",
                "language": "",
                "result_path": None
            } 