from dependency_injector import containers, providers

from .database import Database
from .repositories import TranscriptionRepository, UserRepository
from .services import TranscriptionService, UserService
from .whisper_service import WhisperService

# стандартная залупа с "Dependency Injector with FastAPI and SQLAlchemy."
class Container(containers.DeclarativeContainer):

    wiring_config = containers.WiringConfiguration(modules=[".endpoints"])

    # сейчас этот конфиг юзлес но как пример правильной структуры пойдет
    config = providers.Configuration(yaml_files=["config.yml"])

    db = providers.Singleton(Database, db_url=config.db.url)

    whisper_service = providers.Singleton(WhisperService)

    user_repository = providers.Factory(
        UserRepository,
        session_factory=db.provided.session,
    )

    transcription_repository = providers.Factory(
        TranscriptionRepository,
        session_factory=db.provided.session,
    )

    user_service = providers.Factory(
        UserService,
        user_repository=user_repository,
    )

    transcription_service = providers.Factory(
        TranscriptionService,
        transcription_repository=transcription_repository,
        whisper_service=whisper_service,
    )
