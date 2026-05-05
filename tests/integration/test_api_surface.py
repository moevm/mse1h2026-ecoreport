"""
Проверяем, что инфрастукртура поднялась, основные страницы живы.
"""

import pytest


def _assert_page_is_alive(response, url_name):
    """
    Вспомогательная функция для проверки для HTML-страниц.

    Проверяет:
    1. HTTP 200 — страница доступна
    2. Content-Type начинается с text/html — это действительно страница,
    3. Тело не пустое — шаблон отрендерился
    """
    assert response.status_code == 200, (
        f"Эндпоинт '{url_name}' вернул {response.status_code} вместо 200. "
        f"Если 500 — смотри логи приложения (lifespan, подключение к БД/MinIO)."
    )

    content_type = response.headers.get("content-type", "")
    assert content_type.startswith("text/html"), (
        f"Эндпоинт '{url_name}' отдал не HTML, а '{content_type}'. "
        f"Возможно, роут вернёт JSON или вообще ничего."
    )

    assert len(response.text) > 0, (
        f"Эндпоинт '{url_name}' вернул пустой ответ. "
        f"Вероятно, Jinja2-шаблон пустой или не найден."
    )


class TestMainPage:
    """Главная страница /"""

    def test_status_200(self, client):
        response = client.get("/")
        _assert_page_is_alive(response, "/")


class TestCreatePage:
    """Страница создания отчёта /create"""

    def test_status_200(self, client):
        response = client.get("/create")
        _assert_page_is_alive(response, "/create")

    def test_contains_form_markup(self, client):
        response = client.get("/create")
        assert 'id="full-object-name"' in response.text, (
            "На странице /create не найдено поле 'full-object-name'. "
            "Возможно, Jinja2-шаблоны не подключились."
        )


class TestDocumentsPage:
    """Страница списка отчётов /documents"""

    def test_status_200(self, client):
        response = client.get("/documents")
        _assert_page_is_alive(response, "/documents")

    def test_handles_empty_storage(self, client):
        response = client.get("/documents")
        assert response.status_code == 200, (
            "Страница /documents упала, возможно, MinIO недоступен."
        )


class TestSettingsPage:
    """Страница настроек /settings"""

    def test_status_200(self, client):
        response = client.get("/settings")
        _assert_page_is_alive(response, "/settings")


class TestSwaggerUI:
    """Документация API /docs (автоматически генерируется FastAPI)"""

    def test_status_200(self, client):
        response = client.get("/docs")
        _assert_page_is_alive(response, "/docs")
        