import uuid


class TestGenerateReport:

    def test_status_201_with_valid_data(self, client, valid_report_payload):
        response = client.post("/generate-report", json=valid_report_payload)
        
        assert response.status_code == 201, (
            f"Ожидали 201, получили {response.status_code}. "
            f"Тело ответа: {response.text}"
        )

        assert response.headers.get("content-type") == "application/json", (
            f"Ожидали JSON, получили: {response.headers.get('content-type')}"
        )

        data = response.json()

        assert "status" in data, "В ответе нет поля 'status'"
        assert "report_id" in data, "В ответе нет поля 'report_id'"
        assert isinstance(data["status"], str), f"'status' должен быть строкой, а не {type(data['status'])}"
        assert isinstance(data["report_id"], str), f"'report_id' должен быть строкой, а не {type(data['report_id'])}"
        

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
            f"Тело ответа: {response.text}"
        )

    def test_rejected_with_missing_required_field(self, client, valid_report_payload):
        payload = valid_report_payload.copy()
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

    def test_rejected_with_invalid_type(self, client, valid_report_payload):
        payload = valid_report_payload.copy()
        payload["YEAR"] = "не число"

        response = client.post("/generate-report", json=payload)

        assert response.status_code >= 400, (
            f"Запрос с неверным типом YEAR должен быть отклонён, "
            f"но получили {response.status_code}. "
            f"Тело: {response.text}"
        )
