"""
Общие фикстуры для интеграционных и функциональных тестов.
"""

import io
import os
import pytest
from fastapi.testclient import TestClient
from minio import Minio

from reports.app import create_app
from reports.core.config import settings


@pytest.fixture
def client():
    """
    Фикстура клиента FastAPI.
    Использует TestClient, который позволяет делать запросы к API
    напрямую, минуя реальную сеть. При старте TestClient автоматически
    выполняется блок lifespan (подключение к БД, RabbitMQ, MinIO).
    """
    app = create_app()
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def valid_report_payload():
    """
    Минимальный валидный набор данных.
    Используется как для отправки сырого JSON в интеграционных тестах,
    так и для заполнения полей в браузере в функциональных тестах.
    """
    return {
        "FULL_OBJECT_NAME": "Тестовый объект полное название",
        "SHORT_OBJECT_NAME": "Тестовый объект",
        "YEAR": 2025,
        "ORGANIZATION_NAME": "ООО Тест",
        "REGION": "Москва",
        "RELIEF_TYPE": "Равнинный",
        "SOIL_TYPE": "Суглинок",
        "GROUNDWATER_LEVEL": "2.50",
        "CLIMATE_ZONE": "умеренный континентальный",
        "COORDINATES_LATITUDE": 55.75,
        "COORDINATES_LONGITUDE": 37.61,
        "OBJECT_TYPE": "город",
        "SYSTEM_TYPE": "горизонтальный",
        "PIPE_MATERIAL": "ПВХ",
        "PIPE_DIAMETER": "110.00",
        "PIPE_DEPTH": "1.50",
        "PIPE_LENGTH": "500.00",
        "PIPE_INSTALL_YEAR": 2020,
        "MANHOLE_COUNT": 5,
        "MONITORING_POINT_COUNT": 3,
        "OBSERVATION_POINT": "Точка 1",
        "LATITUDE": 55.756,
        "LONGITUDE": 37.618,
        "MEDIUM_TYPE": "Вода",
        "DESCRIPTION": "Контроль качества",
        "OBSERVATION_FREQUENCY": "Ежемесячно",
        "RESULTS_PH": "7.10",
        "RESULTS_IRON": "0.20",
        "RESULTS_MANGANESE": "0.05",
        "RESULTS_NITRATES": "10.00",
        "RESULTS_SULFATES": "15.00",
        "ORGANIZATION_ADDRESS": "г. Москва, ул. Тестовая, 1",
        "ORGANIZATION_PHONE": "+7 (999) 123-45-67",
        "ORGANIZATION_EMAIL": "test@example.com",
        "RESPONSIBLE_NAME": "Иванов И.И.",
        "RESPONSIBLE_POSITION": "Главный инженер",
        "REPORT_DATE": "2025-03-15",
        "DOCUMENTS_GOST": [],
        "OBSERVATION_POINTS": [],
        "TEST_RESULTS": [],
        "RESULTS_DYNAMIC": [],
        "OBSERVATION_DYNAMICS": [],
    }


@pytest.fixture(scope="function")
def existing_report_id():
    """
    Фикстура подготовки данных.
    Перед запуском тестов на скачивание, эта функция напрямую подключается
    к MinIO и кладет туда фейковый PDF-файл.
    После завершения теста (yield) файл удаляется, чтобы не мусорить в базе.
    """
    report_id = "test-report-fixture"
    bucket_name = settings.MINIO_BUCKET_NAME
    object_name = f"{report_id}.pdf"

    minio_client = Minio(
        f"{settings.MINIO_HOST}:{settings.MINIO_PORT}",
        access_key=settings.MINIO_ROOT_USER.get_secret_value(),
        secret_key=settings.MINIO_ROOT_PASSWORD.get_secret_value(),
        secure=False
    )

    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)

    fake_pdf = b"%PDF-1.4 fake test content for integration testing"
    minio_client.put_object(
        bucket_name=bucket_name,
        object_name=object_name,
        data=io.BytesIO(fake_pdf),
        length=len(fake_pdf),
        content_type="application/pdf"
    )

    yield report_id

    minio_client.remove_object(bucket_name, object_name)
