// функция для чтения данных из таблицы наблюдения
function readObservationPoints() {
    const table = document.getElementById("observation_points_table");
    const points = [];
    if (!table) {
        console.warn("observation_points_table not found");
        return points;
    }

    // все строки в таблице (не только из tbody)
    const rows = Array.from(table.querySelectorAll("tr")).filter(row => {
        const cells = row.querySelectorAll("td");
        return cells.length >= 5; // пропуск заголовков и пустых строк
    });

    // парсинг числовых значений с учетом возможных запятых и пробелов
    const parseNumber = (text) => {
        const value = text.trim().replace(',', '.');
        const number = Number(value);
        return Number.isFinite(number) ? number : text.trim();
    };

    rows.forEach((row) => {
        const cells = row.querySelectorAll("td");
        if (cells.length < 6) return;

        const point = {
            observation_point: cells[1].textContent.trim(),
            latitude: parseNumber(cells[2].textContent),
            longitude: parseNumber(cells[3].textContent),
            medium_type: cells[4].textContent.trim(),
            description: cells[5].textContent.trim(),
        };
        if (point.observation_point || point.medium_type || point.description) {
            points.push(point);
        }
    });

    console.log("Observation points collected:", points);
    return points;
}

// функция для чтения данных из таблицы результатов тестов
function readTestResults() {
    const table = document.getElementById("test_results_table");
    const results = [];
    if (!table) {
        console.warn("test_results_table not found");
        return results;
    }

    const tbody = table.querySelector("tbody");
    if (!tbody) {
        console.warn("test_results_table tbody not found");
        return results;
    }

    const rows = tbody.querySelectorAll("tr");
    console.log("Test results table rows found:", rows.length);

    rows.forEach((row) => {
        const indicator = row.dataset.indicator;
        if (!indicator) {
            console.log("Row skipped - no indicator:", row);
            return; // пропуск строк без indicator
        }

        const inputs = row.querySelectorAll("input[data-field]");
        console.log(`Row for indicator "${indicator}" has ${inputs.length} inputs`);

        const result = {
            indicator: indicator,
            standard: "",
            result: "",
            unit: "",
            compliance: ""
        };

        inputs.forEach((input) => {
            const field = input.dataset.field;
            const value = input.value.trim();
            console.log(`  Input field "${field}" = "${value}"`);

            if (field === "Норматив") result.standard = value;
            else if (field === "Результат") result.result = value;
            else if (field === "Единицы измерения") result.unit = value || "";
            else if (field === "Соответствие") result.compliance = value;
        });

        console.log("Result object:", result);

        const maybeResult = typeof result.result === "string" ? result.result.trim() : String(result.result).trim();
        if (result.indicator && maybeResult !== "") {
            const normalized = maybeResult.replace(',', '.');
            const numeric = parseFloat(normalized);
            if (!Number.isNaN(numeric)) {
                result.result = numeric;
                results.push(result);
            }
        }
    });

    console.log("Test results collected:", results);
    return results;
}

// функция для чтения данных из таблицы динамики наблюдений
function readObservationDynamics() {
    const table = document.getElementById("observation_dynamics_table");
    const dynamics = [];
    if (!table) {
        console.warn("observation_dynamics_table not found");
        return dynamics;
    }

    const tbody = table.querySelector("tbody");
    if (!tbody) {
        console.warn("observation_dynamics_table tbody not found");
        return dynamics;
    }

    const rows = tbody.querySelectorAll("tr");
    console.log("Observation dynamics table rows found:", rows.length);

    const metricKeyMap = {
        "pH": "pH",
        "Железо": "iron",
        "Марганец": "manganese",
        "Нитраты": "nitrates",
        "Сульфаты": "sulfates"
    };

    rows.forEach((row, rowIndex) => {
        const inputs = row.querySelectorAll("input[data-field]");
        console.log(`Row ${rowIndex} has ${inputs.length} inputs`);

        const entry = { date: "" };

        inputs.forEach((input) => {
            const field = input.dataset.field;
            const value = input.value.trim();
            console.log(`  Input field "${field}" = "${value}"`);

            if (field === "Дата") {
                entry.date = value;
            } else {
                const key = metricKeyMap[field] || field;
                entry[key] = value;
            }
        });

        console.log("Entry object:", entry);

        const metrics = ["pH", "iron", "manganese", "nitrates", "sulfates"];
        const hasMetricValue = metrics.some((metric) => {
            return entry[metric] !== undefined && String(entry[metric]).trim() !== "";
        });

        if (entry.date || hasMetricValue) {
            const normalize = (value) => {
                if (value === undefined || value === null || String(value).trim() === "") {
                    return "";
                }
                const normalized = String(value).trim().replace(',', '.');
                const parsed = parseFloat(normalized);
                return Number.isNaN(parsed) ? value : parsed;
            };

            metrics.forEach((metric) => {
                if (entry[metric] !== undefined) {
                    entry[metric] = normalize(entry[metric]);
                }
            });
            dynamics.push(entry);
        }
    });

    console.log("Observation dynamics collected:", dynamics);
    return dynamics;
}
