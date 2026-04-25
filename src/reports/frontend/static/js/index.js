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

// функция для установки ошибки поля
function setFieldError(input, message) {
    if (!input) return;
    input.classList.add("invalid-field");
    input.setAttribute("aria-invalid", "true");
    input.title = message;

    let error = input.nextElementSibling;
    if (!error || !error.classList.contains("field-error")) {
        error = document.createElement("span");
        error.className = "field-error";
        input.parentNode.insertBefore(error, input.nextSibling);
    }
    error.textContent = message;
}

// функция для очистки ошибок поля
function clearFieldError(input) {
    if (!input) return;
    input.classList.remove("invalid-field");
    input.removeAttribute("aria-invalid");
    input.title = "";
    const error = input.nextElementSibling;
    if (error?.classList.contains("field-error")) {
        error.remove();
    }
}

// функция для валидации положительного числа с двумя десятичными знаками
function validatePositiveTwoDecimals(value) {
    const normalized = value.trim().replace(',', '.');
    return /^\d+\.\d{2}$/.test(normalized) && parseFloat(normalized) > 0;
}

// функция для валидации целого положительного числа
function validatePositiveInteger(value) {
    return /^[1-9]\d*$/.test(value.trim());
}

// функция для валидации года (целое положительное число, не больше текущего года)
function validateYear(value) {
    const normalized = value.trim();
    const year = parseInt(normalized, 10);
    const currentYear = new Date().getFullYear();
    return /^[1-9]\d*$/.test(normalized) && year <= currentYear;
}

// функция для валидации даты (не в будущем)
function validateDateNotFuture(value) {
    if (!value) return false;
    const date = new Date(value);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    return !Number.isNaN(date.getTime()) && date <= today;
}

// функция для валидации всех полей формы с помощью заданных правил
function validateFieldInput(field, validator, hint) {
    if (!field) return true;
    const value = field.value.trim();
    if (!value) {
        clearFieldError(field);
        return true;
    }
    const valid = validator(value);
    if (!valid) {
        setFieldError(field, hint);
    } else {
        clearFieldError(field);
    }
    return valid;
}

// функция для привязки валидации к полю по его ID
function attachValidationRule(id, validator, hint) {
    const field = document.getElementById(id);
    if (!field) return;
    field.addEventListener("input", () => validateFieldInput(field, validator, hint));
}

// функция для валидации полей результатов тестов в таблице
function validateTestResultsInput(field) {
    if (!field) return true;
    const value = field.value.trim();
    if (value === "") {
        setFieldError(field, "Заполните результат или отключите показатель");
        return false;
    }
    if (!validatePositiveTwoDecimals(value)) {
        setFieldError(field, "Введите положительное число с двумя знаками после запятой");
        return false;
    }
    clearFieldError(field);
    return true;
}

// функция для валидации полей динамики наблюдений в таблице
function validateObservationDynamicsInput(field) {
    if (!field) return true;
    const fieldName = field.dataset.field;
    const value = field.value.trim();

    if (fieldName === "Дата") {
        if (value === "") {
            setFieldError(field, "Укажите дату");
            return false;
        }
        if (!validateDateNotFuture(value)) {
            setFieldError(field, "Дата не должна быть позже сегодняшнего дня");
            return false;
        }
        clearFieldError(field);
        return true;
    }

    if (value === "") {
        clearFieldError(field);
        return true;
    }
    if (!validatePositiveTwoDecimals(value)) {
        setFieldError(field, "Введите положительное число с двумя знаками после запятой");
        return false;
    }
    clearFieldError(field);
    return true;
}

// общая функция для валидации всех полей таблицы результатов тестов
function validateTestResultsTable() {
    const table = document.getElementById("test_results_table");
    if (!table) return true;
    const tbody = table.querySelector("tbody");
    if (!tbody) return true;

    let valid = true;
    tbody.querySelectorAll("input[data-field='Результат']").forEach((input) => {
        if (!validateTestResultsInput(input)) valid = false;
    });
    return valid;
}

// общая функция для валидации всех полей таблицы динамики наблюдений
function validateObservationDynamicsTable() {
    const table = document.getElementById("observation_dynamics_table");
    if (!table) return true;
    const tbody = table.querySelector("tbody");
    if (!tbody) return true;

    let valid = true;
    tbody.querySelectorAll("tr").forEach((row) => {
        const dateInput = row.querySelector("input[data-field='Дата']");
        const metricInputs = Array.from(row.querySelectorAll("input[data-field]")).filter((input) => input.dataset.field !== "Дата");
        const hasMetric = metricInputs.some((input) => input.value.trim() !== "");

        if (!dateInput || !dateInput.value.trim()) {
            if (hasMetric) {
                setFieldError(dateInput, "Дата обязательна, если введены показатели");
                valid = false;
            }
        } else if (hasMetric && !validateObservationDynamicsInput(dateInput)) {
            valid = false;
        }

        metricInputs.forEach((input) => {
            if (input.value.trim() !== "" && !validateObservationDynamicsInput(input)) {
                valid = false;
            }
        });
    });

    return valid;
}

// функция для валидации полей метаданных отчета
function validateMetadataFields() {
    const rules = [
        { id: "groundwater-level", validator: validatePositiveTwoDecimals, hint: "Укажите положительное число с двумя знаками после запятой" },
        { id: "pipe-diameter", validator: validatePositiveTwoDecimals, hint: "Укажите положительное число с двумя знаками после запятой" },
        { id: "total-length", validator: validatePositiveTwoDecimals, hint: "Укажите положительное число с двумя знаками после запятой" },
        { id: "burial-depth", validator: validatePositiveTwoDecimals, hint: "Укажите положительное число с двумя знаками после запятой" },
        { id: "laying-year", validator: validateYear, hint: `Введите год не больше ${new Date().getFullYear()}` },
        { id: "wells-count", validator: validatePositiveInteger, hint: "Введите целое положительное число" },
        { id: "report-year", validator: validateYear, hint: `Введите год не больше ${new Date().getFullYear()}` },
        { id: "org-phone", validator: validatePhone, hint: "Введите корректный номер телефона" },
        { id: "org-email", validator: validateEmail, hint: "Введите корректный email" },
        { id: "report-date", validator: validateReportDate, hint: "Дата не может быть позже сегодняшнего дня" },
        { id: "monitor-amount", validator: validatePositiveInteger, hint: "Введите целое положительное число" }
    ];

    let valid = true;
    rules.forEach((rule) => {
        const field = document.getElementById(rule.id);
        if (field && !validateFieldInput(field, rule.validator, rule.hint)) {
            valid = false;
        }
    });
    return valid;
}

// функция для общей валидации всех полей формы перед отправкой
function validateAllForm() {
    let valid = true;
    valid = validateMetadataFields() && valid;
    valid = validateTestResultsTable() && valid;
    valid = validateObservationDynamicsTable() && valid;

    if (!valid) {
        const status = document.getElementById("report-status");
        if (status) {
            status.innerText = "Исправьте ошибки в выделенных полях и повторите попытку";
        }
    }

    return valid;
}

// функция для валидации почты
function validateEmail(value) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value.trim());
}

// функция для валидации телефона
function validatePhone(value) {
    const digits = value.replace(/\D/g, "").replace(/^8/, "7");
    return digits.length === 11 && digits.startsWith("7");
}

// функция для валидации даты отчета (не в будущем)
function validateReportDate(value) {
    if (!value) return false;

    // строго ISO формат
    if (!/^\d{4}-\d{2}-\d{2}$/.test(value)) return false;

    const date = new Date(value);
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    return date <= today;
}

// функция для форматирования телефонного номера в процессе ввода
function formatPhone(value) {
    const digits = value.replace(/\D/g, "").replace(/^8/, "7").slice(0, 11);

    let result = "+7";

    if (digits.length > 1) {
        const d = digits.slice(1);

        if (d.length > 0) result += " (" + d.slice(0, 3);
        if (d.length >= 3) result += ") ";

        if (d.length >= 4) result += d.slice(3, 6);
        if (d.length >= 6) result += "-" + d.slice(6, 8);
        if (d.length >= 8) result += "-" + d.slice(8, 10);
    }

    return result;
}

window.addEventListener("load", function () {
    const phoneInput = document.getElementById("org-phone");
    if (!phoneInput) return;

    phoneInput.addEventListener("input", function () {
        const start = phoneInput.selectionStart;

        const oldValue = phoneInput.value;
        const newValue = formatPhone(oldValue);

        phoneInput.value = newValue;

        // нормальный возврат курсора (упрощённый, но рабочий)
        const diff = newValue.length - oldValue.length;
        const newPos = Math.max(0, start + diff);

        phoneInput.setSelectionRange(newPos, newPos);
    });
});

window.addEventListener("load", function () {
    attachValidationRule("groundwater-level", validatePositiveTwoDecimals, "Укажите положительное число с двумя знаками после запятой");
    attachValidationRule("pipe-diameter", validatePositiveTwoDecimals, "Укажите положительное число с двумя знаками после запятой");
    attachValidationRule("total-length", validatePositiveTwoDecimals, "Укажите положительное число с двумя знаками после запятой");
    attachValidationRule("burial-depth", validatePositiveTwoDecimals, "Укажите положительное число с двумя знаками после запятой");
    attachValidationRule("laying-year", validateYear, `Введите год не больше ${new Date().getFullYear()}`);
    attachValidationRule("wells-count", validatePositiveInteger, "Введите целое положительное число");
    attachValidationRule("monitor-amount", validatePositiveInteger, "Введите целое положительное число");
    attachValidationRule("report-year", validateYear, `Введите год не больше ${new Date().getFullYear()}`);
    attachValidationRule("org-phone", validatePhone, "Введите номер в формате +7 (999) 999-99-99");
    attachValidationRule("org-email",validateEmail,"Введите корректный email (example@mail.com)");
    attachValidationRule("report-date",validateReportDate,"Некорректный формат даты");
   
    document.addEventListener("input", function (event) {
        const target = event.target;
        if (!(target instanceof HTMLInputElement)) return;
        if (target.closest("#test_results_table") && target.dataset.field === "Результат") {
            validateTestResultsInput(target);
        }
        if (target.closest("#observation_dynamics_table") && target.dataset.field && target.dataset.field !== "Дата") {
            validateObservationDynamicsInput(target);
        }
    });

    document.addEventListener("change", function (event) {
        const target = event.target;
        if (!(target instanceof HTMLInputElement)) return;
        if (target.closest("#observation_dynamics_table") && target.dataset.field === "Дата") {
            validateObservationDynamicsInput(target);
        }
    });
});

// функция для чтения данных из таблицы пунктов наблюдения
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

        if (entry.date && hasMetricValue) {
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

async function sendForm() {
    if (!validateAllForm()) {
        return;
    }

    const status = document.getElementById("report-status");
    if (status) status.innerText = "Генерация отчета...";

    // Cбор данных из всех известных полей по их ID
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

function clearAllFormFields() {
    console.log("Start clearing forms");

    const allInputs = document.querySelectorAll('#create-report-form input, #create-report-form select');
    allInputs.forEach(field => {
        if (field.type === 'button' || field. type === 'submit' || field.type === 'hidden') {
            return;
        }

        if (field.tagName === 'SELECT') {
            field.selectedIndex = 0;
        } else {
            field.value = '';
        }
    }); 
}

document.addEventListener('DOMContentLoaded', function () {
    const clearButton = document.getElementById('clear-form-button');

    if (clearButton) {
        clearButton.addEventListener('click', function (event) {
            event.preventDefault();
            clearAllFormFields();
        });
    } else {
        console.warn("Кнопка 'Очистить поля' не найдена");
    }
});