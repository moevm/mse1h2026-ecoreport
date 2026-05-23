async function sendForm() {
    if (!validateAllForm()) {
        return;
    }

    const status = document.getElementById("report-status");
    if (status) status.innerText = "Генерация отчета...";

    // сбор данных из всех известных полей по их ID
    const data = {
        // информация об объекте
        FULL_OBJECT_NAME: document.getElementById("full-object-name")?.value || "Объект по умолчанию",
        SHORT_OBJECT_NAME: document.getElementById("short-object-name")?.value || "Объект",
        YEAR: parseInt(document.getElementById("report-year")?.value) || 2026,
        ORGANIZATION_NAME: document.getElementById("organization-name")?.value || "Организация",
        REGION: document.getElementById("region")?.value || "Регион",

        // нормативные документы (из localStorage)
        DOCUMENTS_GOST: JSON.parse(localStorage.getItem("gost_list") || '[]'),

        // природные условия
        RELIEF_TYPE: document.getElementById("relief-type")?.value || "Равнинный",
        SOIL_TYPE: document.getElementById("soil-type")?.value || "Суглинок",
        GROUNDWATER_LEVEL: (document.getElementById("groundwater-level")?.value.trim() || "").replace(',', '.'),
        CLIMATE_ZONE: document.getElementById("climate-zone")?.value || "Умеренный",

        // координаты объекта
        COORDINATES_LATITUDE: parseFloat(document.getElementById("coord-n")?.value) || 55.75,
        COORDINATES_LONGITUDE: parseFloat(document.getElementById("coord-e")?.value) || 37.61,

        // характеристика системы
        OBJECT_TYPE: document.getElementById("object-type")?.value || "город",
        SYSTEM_TYPE: document.getElementById("type-system")?.value || "",
        PIPE_MATERIAL: document.getElementById("pipe-material")?.value.trim() || "",
        PIPE_DIAMETER: (document.getElementById("pipe-diameter")?.value.trim() || "").replace(',', '.'),
        PIPE_DEPTH: (document.getElementById("burial-depth")?.value.trim() || "").replace(',', '.'),
        PIPE_LENGTH: (document.getElementById("total-length")?.value.trim() || "").replace(',', '.'),
        PIPE_INSTALL_YEAR: parseInt(document.getElementById("laying-year")?.value) || 0,
        MANHOLE_COUNT: parseInt(document.getElementById("wells-count")?.value) || 0,

        // мониторинг
        MONITORING_POINT_COUNT: parseInt(document.getElementById("monitor-amount")?.value) || 0,
        OBSERVATION_POINT: document.getElementById("observ-point")?.value || "Точка А",
        LATITUDE: parseFloat(document.getElementById("observ-coord-n")?.value) || 55.756,
        LONGITUDE: parseFloat(document.getElementById("observ-coord-e")?.value) || 37.618,
        MEDIUM_TYPE: document.getElementById("eco-type")?.value || "Вода",
        DESCRIPTION: document.getElementById("description")?.value || "Контроль качества",
        OBSERVATION_FREQUENCY: document.getElementById("observ-period")?.value || "Ежемесячно",
        OBSERVATION_POINTS: readObservationPoints(),

        // текущие результаты (упрощенный сбор, т.к. в форме они в таблице)
        RESULTS_PH: 7.1,
        RESULTS_IRON: 0.2,
        RESULTS_MANGANESE: 0.05,
        RESULTS_NITRATES: 10,
        RESULTS_SULFATES: 15,

        // результаты лабораторных анализов
        TEST_RESULTS: readTestResults(),

        // динамика
        RESULTS_DYNAMIC: [],
        OBSERVATION_DYNAMICS: readObservationDynamics(),

        // контактная информация
        ORGANIZATION_ADDRESS: document.getElementById("org-address")?.value || "Адрес",
        ORGANIZATION_PHONE: document.getElementById("org-phone")?.value || "Телефон",
        ORGANIZATION_EMAIL: document.getElementById("org-email")?.value || "Email",
        RESPONSIBLE_NAME: document.getElementById("resp-name")?.value || "Ответственный",
        RESPONSIBLE_POSITION: document.getElementById("resp-pos")?.value || "Должность",
        REPORT_DATE: document.getElementById("report-date")?.value || new Date().toISOString().split("T")[0]
    };

    console.log("FINAL CHECK BEFORE SENDING");
    console.log("TEST_RESULTS:", data.TEST_RESULTS);
    console.log("OBSERVATION_DYNAMICS:", data.OBSERVATION_DYNAMICS);

    try {
        await fetch("/generate-report", {
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
