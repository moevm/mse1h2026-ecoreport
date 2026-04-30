import pytest
import re 


pytestmark = pytest.mark.functional


class TestCreateReport:
        
    def test_page_loads(self, page):
        page.goto("/create")
        assert page.locator("h1.title", has_text="Новый отчет").is_visible()

        
    def test_validation_error_on_empty_submit(self, page):
        page.goto("/create")
        page.locator("button", has_text="Сгенерировать отчет").click()
            
        first_error = page.locator(".field-error").first
        first_error.wait_for(state="visible", timeout=3000)
            
        assert first_error.is_visible(), "Ожидали появление красного текста с ошибкой валидации"


    def test_create_report_success(self, page, valid_report_payload):
        page.goto("/create")

        input_mapping = {
            "#full-object-name": "FULL_OBJECT_NAME",
            "#short-object-name": "SHORT_OBJECT_NAME",
            "#organization-name": "ORGANIZATION_NAME",
            "#region": "REGION",
            "#report-year": "YEAR",
            "#relief-type": "RELIEF_TYPE",
            "#soil-type": "SOIL_TYPE",
            "#groundwater-level": "GROUNDWATER_LEVEL",
            "#coord-n": "COORDINATES_LATITUDE",
            "#coord-e": "COORDINATES_LONGITUDE",
            "#object-type": "OBJECT_TYPE",
            "#pipe-material": "PIPE_MATERIAL",
            "#pipe-diameter": "PIPE_DIAMETER",
            "#burial-depth": "PIPE_DEPTH",
            "#total-length": "PIPE_LENGTH",
            "#laying-year": "PIPE_INSTALL_YEAR",
            "#wells-count": "MANHOLE_COUNT",
            "#monitor-amount": "MONITORING_POINT_COUNT",
            "#observ-point": "OBSERVATION_POINT",
            "#observ-period": "OBSERVATION_FREQUENCY",
            "#org-address": "ORGANIZATION_ADDRESS",
            "#org-email": "ORGANIZATION_EMAIL",
            "#org-phone": "ORGANIZATION_PHONE",
            "#resp-name": "RESPONSIBLE_NAME",
            "#resp-pos": "RESPONSIBLE_POSITION",
            "#report-date": "REPORT_DATE",
        }

        table_mapping = {
            "pH": "RESULTS_PH",
            "Железо": "RESULTS_IRON",
            "Марганец": "RESULTS_MANGANESE",
            "Нитраты": "RESULTS_NITRATES",
            "Сульфаты": "RESULTS_SULFATES",
        }

        # Выпадающие списки (select) заполняются другой командой в Playwright
        select_mapping = {
            "#type-system": "SYSTEM_TYPE",
            "#climate-zone": "CLIMATE_ZONE",
        }

        for html_id, json_key in input_mapping.items():
            value_to_type = str(valid_report_payload[json_key])
            page.fill(html_id, value_to_type)
        
        for html_id, json_key in select_mapping.items():
            value_to_select = str(valid_report_payload[json_key])
            page.select_option(html_id, value_to_select)

        for indicator, json_key in table_mapping.items():
            value_to_fill = str(valid_report_payload[json_key])
            locator = f"tr[data-indicator='{indicator}'] input[data-field='Результат']"
            page.locator(locator).fill(value_to_fill)

        with page.expect_response(lambda response: "/generate-report" in response.url and response.request.method == "POST") as response_info:
            page.locator("button", has_text="Сгенерировать отчет").click()

        
        response = response_info.value
        assert response.status == 201, f"Бэкенд вернул ошибку: {response.status}"

        json_data = response.json()
        assert json_data["status"] == "success", "Ожидали success от сервера"
        