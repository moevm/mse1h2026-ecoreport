async function importFromFile() {
    const fileInput = document.getElementById("file-upload");
    const statusEl = document.getElementById("import-status");

    // Сохраняем ссылку на файл ДО сброса формы — clearAllFormFields очищает input[type=file]
    if (!fileInput || !fileInput.files.length) {
        if (statusEl) statusEl.innerText = "Выберите файл!";
        return;
    }
    const file = fileInput.files[0];

    clearAllFormFields();

    const formData = new FormData();
    formData.append("file", file);

    if (statusEl) statusEl.innerText = "Загрузка...";

    try {
        const response = await fetch("/upload", {
            method: "POST",
            body: formData,
        });

        const result = await response.json();

        if (response.ok && result.status === "success") {
            fillFormFromImport(result.data);
            if (statusEl) statusEl.innerText = "Данные успешно импортированы";
        } else {
            const msg = result.detail || result.message || "неизвестная ошибка";
            if (statusEl) statusEl.innerText = "Ошибка: " + msg;
        }
    } catch (error) {
        if (statusEl) statusEl.innerText = "Ошибка соединения: " + error.message;
    }
}

function fillFormFromImport(data) {
    const fieldMap = {
        FULL_OBJECT_NAME:       "full-object-name",
        SHORT_OBJECT_NAME:      "short-object-name",
        YEAR:                   "report-year",
        ORGANIZATION_NAME:      "organization-name",
        REGION:                 "region",
        RELIEF_TYPE:            "relief-type",
        SOIL_TYPE:              "soil-type",
        GROUNDWATER_LEVEL:      "groundwater-level",
        CLIMATE_ZONE:           "climate-zone",
        COORDINATES_LATITUDE:   "coord-n",
        COORDINATES_LONGITUDE:  "coord-e",
        OBJECT_TYPE:            "object-type",
        SYSTEM_TYPE:            "type-system",
        PIPE_MATERIAL:          "pipe-material",
        PIPE_DIAMETER:          "pipe-diameter",
        PIPE_DEPTH:             "burial-depth",
        PIPE_LENGTH:            "total-length",
        PIPE_INSTALL_YEAR:      "laying-year",
        MANHOLE_COUNT:          "wells-count",
        MONITORING_POINT_COUNT: "monitor-amount",
        OBSERVATION_POINT:      "observ-point",
        LATITUDE:               "observ-coord-n",
        LONGITUDE:              "observ-coord-e",
        MEDIUM_TYPE:            "eco-type",
        DESCRIPTION:            "description",
        OBSERVATION_FREQUENCY:  "observ-period",
        ORGANIZATION_ADDRESS:   "org-address",
        ORGANIZATION_PHONE:     "org-phone",
        ORGANIZATION_EMAIL:     "org-email",
        RESPONSIBLE_NAME:       "resp-name",
        RESPONSIBLE_POSITION:   "resp-pos",
        REPORT_DATE:            "report-date",
    };

    const decimalFields = new Set(["GROUNDWATER_LEVEL", "PIPE_DIAMETER", "PIPE_DEPTH", "PIPE_LENGTH"]);
    for (const [field, elementId] of Object.entries(fieldMap)) {
        if (data[field] !== undefined && data[field] !== null) {
            const el = document.getElementById(elementId);
            if (el) {
                const raw = String(data[field]);
                el.value = decimalFields.has(field) ? (formatTwoDecimals(raw) ?? raw) : raw;
            }
        }
    }

    // ГОСТ: обновить localStorage и состояние кнопок
    if (Array.isArray(data.DOCUMENTS_GOST) && data.DOCUMENTS_GOST.length > 0) {
        localStorage.setItem("gost_list", JSON.stringify(data.DOCUMENTS_GOST));
        document.querySelectorAll("#gost_list .list_element").forEach((btn) => {
            const active = data.DOCUMENTS_GOST.includes(btn.textContent.trim());
            btn.classList.toggle("list_element--active", active);
        });
    }

    // Таблица точек наблюдения
    if (Array.isArray(data.OBSERVATION_POINTS) && data.OBSERVATION_POINTS.length > 0) {
        const tbody = document.querySelector("#observation_points_table tbody");
        if (tbody) {
            tbody.innerHTML = "";
            let rowNum = 1;
            data.OBSERVATION_POINTS.forEach((point) => {
                const lat = parseFloat(String(point.latitude ?? "").replace(",", "."));
                const lon = parseFloat(String(point.longitude ?? "").replace(",", "."));
                // Пропускаем строки без числовых широты и долготы
                if (isNaN(lat) || isNaN(lon)) return;

                const row = document.createElement("tr");
                [
                    rowNum++,
                    point.observation_point || "",
                    lat,
                    lon,
                    point.medium_type || "",
                    point.description || "",
                ].forEach((val) => {
                    const cell = document.createElement("td");
                    cell.textContent = val;
                    row.appendChild(cell);
                });
                tbody.appendChild(row);
            });
        }
    }

    // Таблица результатов лабораторных анализов
    if (Array.isArray(data.TEST_RESULTS) && data.TEST_RESULTS.length > 0) {
        const tbody = document.querySelector("#test_results_table tbody");
        if (tbody) {
            data.TEST_RESULTS.forEach((item) => {
                const row = tbody.querySelector(`tr[data-indicator="${item.indicator}"]`);
                if (!row) return;
                const resultInput = row.querySelector("input[data-field='Результат']");
                if (resultInput) {
                    const raw = item.result !== undefined ? String(item.result) : "";
                    resultInput.value = raw ? (formatTwoDecimals(raw) ?? raw) : "";
                    resultInput.dispatchEvent(new Event("change", { bubbles: true }));
                }
            });
        }
    }

    // Таблица динамики наблюдений
    if (Array.isArray(data.OBSERVATION_DYNAMICS) && data.OBSERVATION_DYNAMICS.length > 0) {
        const tbody = document.querySelector("#observation_dynamics_table tbody");
        if (tbody) {
            tbody.innerHTML = "";
            const metricToLabel = { pH: "pH", iron: "Железо", manganese: "Марганец", nitrates: "Нитраты", sulfates: "Сульфаты" };
            const labels = ["Дата", "pH", "Железо", "Марганец", "Нитраты", "Сульфаты"];
            data.OBSERVATION_DYNAMICS.forEach((entry) => {
                const row = document.createElement("tr");
                labels.forEach((label) => {
                    const cell = document.createElement("td");
                    const input = document.createElement("input");
                    input.type = label === "Дата" ? "date" : "text";
                    input.dataset.field = label;
                    if (label === "Дата") {
                        input.value = entry.date || "";
                    } else {
                        const key = Object.entries(metricToLabel).find(([, v]) => v === label)?.[0];
                        if (key && entry[key] !== undefined) {
                            const raw = String(entry[key]);
                            input.value = formatTwoDecimals(raw) ?? raw;
                        } else {
                            input.value = "";
                        }
                    }
                    cell.appendChild(input);
                    row.appendChild(cell);
                });
                tbody.appendChild(row);
            });
        }
    }
}
