from contextlib import asynccontextmanager
from fastapi import FastAPI

from reports.api.page import page_router
from reports.api.report import reports_router
from reports.api.user import user_router
from reports.infrastructure.rabbitmq.broker import broker
from reports.domain import report_worker  # noqa: F401  registers @broker.subscriber handlers
from reports.core.providers.setup import container
from dishka.integrations.fastapi import setup_dishka
from reports.infrastructure.minio.client import MinioClient
from reports.core.config import settings
from fastapi.staticfiles import StaticFiles
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    await broker.start()

    async with container() as c:
        minio_client = await c.get(MinioClient)
        minio_client.ensure_bucket(settings.MINIO_BUCKET_NAME)

    yield
    await broker.close()

def create_app() -> FastAPI:
    app = FastAPI(
        title="EcoReport",
        lifespan=lifespan
    )

    app.include_router(page_router, tags=["Page"])
    app.include_router(reports_router, tags=["Report"])
    app.include_router(user_router, tags=["User"])

    app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "frontend", "static")), name="static")

    setup_dishka(container, app)

    return app

# app = create_app()
