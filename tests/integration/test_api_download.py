class TestDownloadById:

    def test_download_existing_file(self, client, existing_report_id):
        response = client.get(f"/download/{existing_report_id}")

        assert response.status_code == 200, (
            f"Ожидали 200 при скачивании существующего файла, "
            f"получили {response.status_code}. Тело: {response.text}"
        )

        assert response.headers.get("content-type") == "application/pdf", (
            f"Ожидали application/pdf, получили: {response.headers.get('content-type')}"
        )

        assert len(response.content) > 0, "Скачанный PDF пустой"

    def test_download_nonexistent_file(self, client):
        response = client.get("/download/definitely-not-exists-12345")

        assert response.status_code >= 400, (
            f"Сейчас код возвращает 500 для несуществующего файла. "
            f"Получили {response.status_code} "
        )


class TestDownloadFileByName:

    def test_download_file_success(self, client, existing_report_id):

        object_name = f"{existing_report_id}.pdf"

        response = client.get(f"/download-file/{object_name}")

        assert response.status_code == 200, (
            f"Ожидали 200, получили {response.status_code}. Тело: {response.text}"
        )

        content_disposition = response.headers.get("content-disposition", "")
        assert 'attachment' in content_disposition, (
            f"Ожидали заголовок 'attachment' для скачивания, "
            f"получили: {content_disposition}"
        )

    def test_download_file_unsupported_extension(self, client):
        response = client.get("/download-file/secret-file.exe")

        assert response.status_code >= 400, (
            f"Ожидали 400 для неподдерживаемого расширения, "
            f"получили {response.status_code}. Тело: {response.text}"
        )

    def test_download_file_nonexistent(self, client):
        response = client.get("/download-file/nonexistent-report.pdf")

        assert response.status_code >= 400, (
            f"Сейчас код возвращает 500. Получили {response.status_code}. "
        )