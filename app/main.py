from contextlib import asynccontextmanager
from fastapi import FastAPI
from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka

from app.api.endpoints import router
from app.infrastructure.rabbit.rabbit_provider import rabbit_provider
from app.services.workers.manager import WorkerManager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Контекстный менеджер жизненного цикла приложения.
    Отвечает за запуск и остановку фоновых воркеров при старте и завершении приложения.
    """
    worker_manager = await app.state.dishka_container.get(WorkerManager)
    await worker_manager.start_all()
    yield
    await worker_manager.stop_all()


def create_app() -> FastAPI:
    """
    Фабрика для создания и настройки экземпляра приложения FastAPI.
    Включает роутеры, настраивает DI-контейнер Dishka и задает жизненный цикл.

    :return: Настроенный экземпляр FastAPI.
    """
    app = FastAPI(lifespan=lifespan)
    app.include_router(router)
    
    container = make_async_container(rabbit_provider)
    setup_dishka(container, app)
    
    return app

app = create_app()
