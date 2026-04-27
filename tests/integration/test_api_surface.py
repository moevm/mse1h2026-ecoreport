import pytest


def _assert_page_is_alive(response, url_name):
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
    def test_status_200(self, client):
        response = client.get("/")
        _assert_page_is_alive(response, "/")

    def test_not_empty(self, client):
        response = client.get("/")
        assert len(response.text) > 0, "Главная страница вернула пустоту."


class TestCreatePage:
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
    def test_status_200(self, client):
        response = client.get("/documents")
        _assert_page_is_alive(response, "/documents")

    def test_handles_empty_storage(self, client):
        response = client.get("/documents")
        assert response.status_code == 200, (
            "Страница /documents упала, возможно, MinIO недоступен."
        )


class TestSettingsPage:
    def test_status_200(self, client):
        response = client.get("/settings")
        _assert_page_is_alive(response, "/settings")


class TestSwaggerUI:
    def test_status_200(self, client):
        response = client.get("/docs")
        _assert_page_is_alive(response, "/docs")