"""Application module."""

import logging
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .containers import Container
from . import endpoints


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

container = Container()
app = FastAPI(title="Whisper Transcriptin")

# хуйня какая то но вроде надо для безопасности
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(endpoints.router)
app.container = container

@app.on_event("startup")
async def startup():
    await app.container.db().create_database()
