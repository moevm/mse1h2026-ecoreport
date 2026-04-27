import uuid


MINIMAL_VALID_REPORT_DATA = {
    # --- Информация об объекте ---
    "FULL_OBJECT_NAME": "Тестовый объект полное название",
    "SHORT_OBJECT_NAME": "Тестовый объект",
    "YEAR": 2025,
    "ORGANIZATION_NAME": "ООО Тест",
    "REGION": "Москва",

    # --- Природные условия ---
    "RELIEF_TYPE": "Равнинный",
    "SOIL_TYPE": "Суглинок",
    "GROUNDWATER_LEVEL": "2.50",
    "CLIMATE_ZONE": "умеренный континентальный",

    # --- Координаты ---
    "COORDINATES_LATITUDE": 55.75,
    "COORDINATES_LONGITUDE": 37.61,

    # --- Характеристика дренажной системы ---
    "OBJECT_TYPE": "город",
    "SYSTEM_TYPE": "горизонтальный",
    "PIPE_MATERIAL": "ПВХ",
    "PIPE_DIAMETER": "110.00",
    "PIPE_DEPTH": "1.50",
    "PIPE_LENGTH": "500.00",
    "PIPE_INSTALL_YEAR": 2020,
    "MANHOLE_COUNT": 5,

    # --- Мониторинг ---
    "MONITORING_POINT_COUNT": 3,
    "OBSERVATION_POINT": "Точка 1",
    "LATITUDE": 55.756,
    "LONGITUDE": 37.618,
    "MEDIUM_TYPE": "Вода",
    "DESCRIPTION": "Контроль качества",
    "OBSERVATION_FREQUENCY": "Ежемесячно",

    # --- Текущие результаты анализов ---
    "RESULTS_PH": 7.1,
    "RESULTS_IRON": 0.2,
    "RESULTS_MANGANESE": 0.05,
    "RESULTS_NITRATES": 10.0,
    "RESULTS_SULFATES": 15.0,

    # --- Контактная информация ---
    "ORGANIZATION_ADDRESS": "г. Москва, ул. Тестовая, 1",
    "ORGANIZATION_PHONE": "+7 (999) 123-45-67",
    "ORGANIZATION_EMAIL": "test@example.com",
    "RESPONSIBLE_NAME": "Иванов И.И.",
    "RESPONSIBLE_POSITION": "Главный инженер",
    "REPORT_DATE": "2025-03-15",

    # --- Списки (необязательные, но Pydantic ожидает их наличия) ---
    "DOCUMENTS_GOST": [],
    "OBSERVATION_POINTS": [],
    "TEST_RESULTS": [],
    "RESULTS_DYNAMIC": [],
    "OBSERVATION_DYNAMICS": [],
}


class TestGenerateReport:

    def test_status_201_with_valid_data(self, client):
        response = client.post("/generate-report", json=MINIMAL_VALID_REPORT_DATA)
        
        assert response.status_code == 201, (
            f"Ожидали 201, получили {response.status_code}. "
            f"Тело ответа: {response.text}"
        )

        assert isinstance(data, dict), f"Ожидали JSON-объект, получили: {type(data)}"

        assert "status" in data, "В ответе нет поля 'status'"

        assert "report_id" in data, "В ответе нет поля 'report_id'"

        assert isinstance(data["status"], str), f"'status' должен быть строкой, а не {type(data['status'])}"
        assert isinstance(data["report_id"], str), f"'report_id' должен быть строкой, а не {type(data['report_id'])}"
        
        data = response.json()

        assert data.get("status") == "success", (
            f"Ожидали status='success', получили: {data.get('status')}"
        )

        report_id = data.get("report_id")
        assert report_id is not None, "В ответе нет поля report_id"

        allowed_keys = {"status", "report_id"}
        actual_keys = set(data.keys())
        extra_keys = actual_keys - allowed_keys
        assert not extra_keys, f"В ответе неожиданные поля: {extra_keys}"

        try:
            uuid.UUID(report_id)
        except ValueError:
            assert False, f"report_id не является валидным UUID: {report_id}"

    def test_rejected_with_empty_body(self, client):
        response = client.post("/generate-report", json={})

        assert response.status_code >= 400, (
            f"Пустое тело должно быть отклонено, но получили {response.status_code}. "
            f"Это значит, сервер принял мусор за хорошие данные. "
            f"Тело ответа: {response.text}"
        )

    def test_rejected_with_missing_required_field(self, client):
        payload = MINIMAL_VALID_REPORT_DATA.copy()
        del payload["FULL_OBJECT_NAME"]

        response = client.post("/generate-report", json=payload)

        assert response.status_code >= 400, (
            f"Запрос без FULL_OBJECT_NAME должен быть отклонён, "
            f"но получили {response.status_code}. "
            f"Тело: {response.text}"
        )

        assert response.headers.get("content-type", "").startswith("application/json"), (
        f"Ожидали JSON с ошибкой, получили: {response.headers.get('content-type')}"
    )

    def test_rejected_with_invalid_type(self, client):
        payload = MINIMAL_VALID_REPORT_DATA.copy()
        payload["YEAR"] = "не число"

        response = client.post("/generate-report", json=payload)

        assert response.status_code >= 400, (
            f"Запрос с неверным типом YEAR должен быть отклонён, "
            f"но получили {response.status_code}. "
            f"Тело: {response.text}"
        )
