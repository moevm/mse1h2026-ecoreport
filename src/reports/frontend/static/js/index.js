async function uploadFile() {
    const fileInput = document.getElementById("file-input");
    const status = document.getElementById("upload-status");

    if (!fileInput.files.length) {
        status.innerText = "Выберите файл!";
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    status.innerText = "Загрузка...";

    try {
        const response = await fetch("/upload", {
            method: "POST",
            body: formData
        });

        const result = await response.json();

        if (result.status === "success") {
            status.innerText = "Файл успешно загружен";
            console.log(result.saved_as);

        } else {
            status.innerText = "Ошибка: " + result.message;
        }

    } catch (error) {
        status.innerText = "Ошибка соединения";
    }
}

async function sendForm() {
    const status = document.getElementById("report-status");
    if (status) status.innerText = "Генерация отчета...";

    // Сбор данных из всех известных полей по их ID (на основе ReportInputData)
    const data = {
        // Информация об объекте
        FULL_OBJECT_NAME: document.getElementById("full-object-name")?.value || "Объект по умолчанию",
        SHORT_OBJECT_NAME: document.getElementById("short-object-name")?.value || "Объект",
        YEAR: parseInt(document.getElementById("report-year")?.value) || 2026,
        ORGANIZATION_NAME: document.getElementById("organization-name")?.value || "Организация",
        REGION: document.getElementById("region")?.value || "Регион",

        // Нормативные документы (из localStorage, как делает gost.js)
        DOCUMENTS_GOST: JSON.parse(localStorage.getItem("gost_list") || '[]'),

        // Природные условия
        RELIEF_TYPE: document.getElementById("relief-type")?.value || "Равнинный",
        SOIL_TYPE: document.getElementById("soil-type")?.value || "Суглинок",
        GROUNDWATER_LEVEL: document.getElementById("groundwater-level")?.value || "2.5 м",
        CLIMATE_ZONE: document.getElementById("climate-zone")?.value || "Умеренный",

        // Координаты объекта
        COORDINATES_LATITUDE: parseFloat(document.getElementById("coord-n")?.value) || 55.75,
        COORDINATES_LONGITUDE: parseFloat(document.getElementById("coord-e")?.value) || 37.61,

        // Характеристика системы
        OBJECT_TYPE: document.getElementById("object-type")?.value || "город",
        SYSTEM_TYPE: document.getElementById("system-type")?.value || "Дренажная",
        PIPE_MATERIAL: document.getElementById("pipe-material")?.value || "Пластик ПВХ",
        PIPE_DIAMETER: document.getElementById("pipe-diameter")?.value || "500 мм",
        PIPE_DEPTH: document.getElementById("pipe-depth")?.value || "2 м",
        PIPE_LENGTH: document.getElementById("pipe-length")?.value || "1000 м",
        PIPE_INSTALL_YEAR: parseInt(document.getElementById("pipe-install-year")?.value) || 2010,
        MANHOLE_COUNT: parseInt(document.getElementById("manhole-count")?.value) || 10,

        // Мониторинг
        MONITORING_POINT_COUNT: parseInt(document.getElementById("monitor-amount")?.value) || 5,
        OBSERVATION_POINT: document.getElementById("observ-point")?.value || "Точка А",
        LATITUDE: parseFloat(document.getElementById("observ-coord-n")?.value) || 55.756,
        LONGITUDE: parseFloat(document.getElementById("observ-coord-e")?.value) || 37.618,
        MEDIUM_TYPE: document.getElementById("eco-type")?.value || "Вода",
        DESCRIPTION: document.getElementById("description")?.value || "Контроль качества",
        OBSERVATION_FREQUENCY: document.getElementById("observ-period")?.value || "Ежемесячно",

        // Текущие результаты (упрощенный сбор, т.к. в форме они в таблице)
        RESULTS_PH: 7.1,
        RESULTS_IRON: 0.2,
        RESULTS_MANGANESE: 0.05,
        RESULTS_NITRATES: 10,
        RESULTS_SULFATES: 15,

        // Динамика (пустой список для примера, т.к. сбор из таблицы сложен)
        RESULTS_DYNAMIC: [],

        // Контактная информация
        ORGANIZATION_ADDRESS: document.getElementById("org-address")?.value || "Адрес",
        ORGANIZATION_PHONE: document.getElementById("org-phone")?.value || "Телефон",
        ORGANIZATION_EMAIL: document.getElementById("org-email")?.value || "Email",
        RESPONSIBLE_NAME: document.getElementById("resp-name")?.value || "Ответственный",
        RESPONSIBLE_POSITION: document.getElementById("resp-pos")?.value || "Должность",
        REPORT_DATE: document.getElementById("report-date")?.value || new Date().toLocaleDateString()
    };

    try {
        const response = await fetch("/generate-report", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (result.status === "success") {
            const downloadUrl = `/download/${result.report_id}`;

            status.innerHTML = `
                Отчет готов!
                <a href="${downloadUrl}" target="_blank"
                   style="color: #5050f5; text-decoration: underline;">
                   Скачать PDF
                </a>
            `;
        } else {
            status.innerText = "Ошибка: " + result.message;
        }
    } catch (error) {
        status.innerText = "Ошибка соединения: " + error.message;
    }
}

window.addEventListener('load', function () {
    const site_type_input = document.getElementById("site-type");
    const bog_extra = document.getElementById("bog-extra");
    const urban_extra = document.getElementById("urban-extra");
    const protected_extra = document.getElementById("protected-extra");
    site_type_input.addEventListener('input', function() {
        bog_extra.hidden = true;
        urban_extra.hidden = true;
        protected_extra.hidden = true;
        switch (site_type_input.value){
            case "bog":
                bog_extra.hidden = false;
                break;
            case "urban":
                urban_extra.hidden = false;
                break;
            case "protected":
                protected_extra.hidden = false;
                break;
            default:
                break;
    
        }
    
    });
})
