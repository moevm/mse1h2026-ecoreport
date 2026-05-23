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


// функция для привязки валидации к полю по его ID
function attachValidationRule(id, validator, hint) {
    const field = document.getElementById(id);
    if (!field) return;
    field.addEventListener("input", () => validateFieldInput(field, validator, hint));
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

// Прикрепление валидаторов для полей
function attachAllValidationRules() {
    attachValidationRule("groundwater-level", validatePositiveTwoDecimals, "Укажите положительное число с двумя знаками после запятой");
    attachValidationRule("pipe-diameter", validatePositiveTwoDecimals, "Укажите положительное число с двумя знаками после запятой");
    attachValidationRule("total-length", validatePositiveTwoDecimals, "Укажите положительное число с двумя знаками после запятой");
    attachValidationRule("burial-depth", validatePositiveTwoDecimals, "Укажите положительное число с двумя знаками после запятой");
    attachValidationRule("laying-year", validateYear, `Введите год не больше ${new Date().getFullYear()}`);
    attachValidationRule("wells-count", validatePositiveInteger, "Введите целое положительное число");
    attachValidationRule("monitor-amount", validatePositiveInteger, "Введите целое положительное число");
    attachValidationRule("report-year", validateYear, `Введите год не больше ${new Date().getFullYear()}`);
    attachValidationRule("org-phone", validatePhone, "Введите номер в формате +7 (999) 999-99-99");
    attachValidationRule("org-email", validateEmail, "Введите корректный email (example@mail.com)");
    attachValidationRule("report-date", validateReportDate, "Некорректный формат даты");
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

window.addEventListener("load", function () {
    attachAllValidationRules()
}
