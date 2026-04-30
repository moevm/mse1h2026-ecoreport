import pytest


pytestmark = pytest.mark.functional


class TestDocuments:

    def test_documents_page_shows_reports(self, page, existing_report_id):
        page.goto("/documents")
        
        page.locator("h1.title", has_text="Отчеты").wait_for(state="visible", timeout=5000)

        cards = page.locator("article.card")
        assert cards.count() > 0, "На странице нет отчётов"
        
        pdf_button = cards.first.locator("a", has_text="Скачать PDF")
        assert pdf_button.is_visible(), "Кнопка 'Скачать PDF' не найдена в карточке"

    def test_download_pdf(self, page, existing_report_id):
        page.goto("/documents")

        with page.expect_download() as download_info:
            page.locator("a", has_text="Скачать PDF").first.click()
        
        download = download_info.value

        filename = download.suggested_filename
        assert filename.endswith(".pdf"), (
            f"Ожидали PDF, получили: {filename}"
        )
        
        assert download.path().stat().st_size > 0, "Скачанный файл пустой"
