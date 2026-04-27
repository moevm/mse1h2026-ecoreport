class TestMainPage:
    def test_status_200(self, client):
        response = client.get("/")
        assert response.status_code == 200, (
            f"Ожидали 200, получили {response.status_code}. "
            f"Проверь lifespan и роут '/'."
        )

    def test_content_type_html(self, client):
        response = client.get("/")
        content_type = response.headers.get("content-type", "")
        assert content_type.startswith("text/html"), (
            f"Ожидали HTML, получили: '{content_type}'."
        )

    def test_not_empty(self, client):
        response = client.get("/")
        assert len(response.text) > 0, "Ответ пустой."


class TestCreatePage:
    def test_status_200(self, client):
        response = client.get("/create")
        assert response.status_code == 200, (
            f"Ожидали 200, получили {response.status_code}. "
            f"Проверь роут '/create' и Jinja2-контекст."
        )

    def test_content_type_html(self, client):
        response = client.get("/create")
        content_type = response.headers.get("content-type", "")
        assert content_type.startswith("text/html"), (
            f"Ожидали HTML, получили: '{content_type}'."
        )

    def test_not_empty(self, client):
        response = client.get("/create")
        assert len(response.text) > 0, "Ответ пустой."


class TestDocumentsPage:
    def test_status_200(self, client):
        response = client.get("/documents")
        assert response.status_code == 200, (
            f"Ожидали 200, получили {response.status_code}. "
            f"Проверь роут '/documents' и подключение к MinIO."
        )

    def test_content_type_html(self, client):
        response = client.get("/documents")
        content_type = response.headers.get("content-type", "")
        assert content_type.startswith("text/html"), (
            f"Ожидали HTML, получили: '{content_type}'."
        )

    def test_not_empty(self, client):
        response = client.get("/documents")
        assert len(response.text) > 0, "Ответ пустой."


class TestSettingsPage:
    def test_status_200(self, client):
        response = client.get("/settings")
        assert response.status_code == 200

    def test_content_type_html(self, client):
        response = client.get("/settings")
        content_type = response.headers.get("content-type", "")
        assert content_type.startswith("text/html"), (
            f"Ожидали HTML, получили: '{content_type}'."
        )

    def test_not_empty(self, client):
        response = client.get("/settings")
        assert len(response.text) > 0, "Ответ пустой."


class TestSwaggerUI:
    def test_status_200(self, client):
        response = client.get("/docs")
        assert response.status_code == 200, (
            f"Ожидали 200, получили {response.status_code}. "
            f"Проверь старт приложения и схему."
        )

    def test_content_type_html(self, client):
        response = client.get("/docs")
        content_type = response.headers.get("content-type", "")
        assert content_type.startswith("text/html"), (
            f"Ожидали HTML, получили: '{content_type}'."
        )

    def test_not_empty(self, client):
        response = client.get("/docs")
        assert len(response.text) > 0, "Swagger UI отдал пустой ответ."
        