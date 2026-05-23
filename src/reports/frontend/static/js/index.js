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

        // возврат курсора 
        const diff = newValue.length - oldValue.length;
        const newPos = Math.max(0, start + diff);

        phoneInput.setSelectionRange(newPos, newPos);
    });
});

window.addEventListener("load", function () {
    attachAllValidationRules()

    document.addEventListener("input", function (event) {
        const target = event.target;
        if (!(target instanceof HTMLInputElement)) return;

        // обработка полей "Результат" в таблице тестов
        if (target.closest("#test_results_table") && target.dataset.field === "Результат") {
            // замена запятой на точки прямо в поле ввода
            const oldValue = target.value;
            const newValue = oldValue.replace(/,/g, '.');
            if (newValue !== oldValue) {
                // сохранение позиции курсора
                const cursorPos = target.selectionStart;
                target.value = newValue;
                target.setSelectionRange(cursorPos, cursorPos);
            }

            // валидация введенного значения
            validateTestResultsInput(target);

            // автоматическое обновление ячейки "Соответствие" в той же строке
            const row = target.closest("tr");
            if (row && row.dataset.indicator) {
                const complianceInput = row.querySelector("input[data-field='Соответствие']");
                if (complianceInput) {
                    complianceInput.value = compareWithStandard(row.dataset.indicator, target.value);
                }
            }
        }

        // обработка полей динамики наблюдений
        if (target.closest("#observation_dynamics_table") && target.dataset.field && target.dataset.field !== "Дата") {
            // замена запятой на точку
            const oldValue = target.value;
            const newValue = oldValue.replace(/,/g, '.');
            if (newValue !== oldValue) {
                const cursorPos = target.selectionStart;
                target.value = newValue;
                target.setSelectionRange(cursorPos, cursorPos);
            }
            // валидация введенного значения
            validateObservationDynamicsInput(target);
        }
    });

    // отдельный обработчик change для поля "Дата" в таблице динамика наблюдений
    document.addEventListener("change", function (event) {
        const target = event.target;
        if (!(target instanceof HTMLInputElement)) return;
        if (target.closest("#observation_dynamics_table") && target.dataset.field === "Дата") {
            validateObservationDynamicsInput(target);
        }
    });

});

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


// функция для очистки всех полей на странице создания отчета
function clearAllFormFields() {
    console.log("Start clearing forms");
    
    // 1. Очищаем обычные поля ввода и select
    const regularFields = document.querySelectorAll(`
        input:not([type="button"]):not([type="submit"]):not([type="hidden"]),
        select
    `);
    
    // не трогаем поля внутри таблиц
    regularFields.forEach(field => {
        if (field.closest('table')) return;

        if (field.tagName === 'SELECT') {
            field.selectedIndex = 0;
        } else {
            field.value = '';
        }
    });


    // 2. Очистка таблиц
    // --------------------------
    // Таблица "Точки наблюдения"
    const pointsTbody = document.querySelector('#observation_points_table tbody');
    if (pointsTbody) {
        pointsTbody.innerHTML = '';
    }

    const testResultsTbody = document.querySelector('#test_results_table tbody');
    if (testResultsTbody) {
        const resultInputs = testResultsTbody.querySelectorAll('input[data-field="Результат"]');

        resultInputs.forEach(input => {
            const oldValue = input.value;
            input.value = '';

            // Обновляем поле "Соответствие" после очищения таблицы
            if (oldValue !== '') {
                const changeEvent = new Event('change', { bubbles: true });
                input.dispatchEvent(changeEvent);
            }
        });
    }

    // Таблица "Динамика наблюдений"
    const dynamicsTbody = document.querySelector('#observation_dynamics_table tbody');
    if (dynamicsTbody) {
        dynamicsTbody.innerHTML = '';
    }

    // 3. Сброс кнопок ГОСТов
    const gostButtons = document.querySelectorAll('#gost_list .list_element');
    gostButtons.forEach(btn => {
        btn.classList.remove('list_element--active');
        btn.dataset.selected = "false";
    });

    // 4. Сброс синих кнопок (pH, Железо, Марганец и т.д.)
    const toggleButtons = document.querySelectorAll('.list_element:not(#gost_list .list_element)');
    toggleButtons.forEach(button => {
        button.dataset.selected = "false";
        button.classList.add('list_element--active');
    });
    toggleButtons.forEach(button => button.click());

    // 5. Очистка ошибок валидации
    document.querySelectorAll('.invalid-field').forEach(el => {
        el.classList.remove('invalid-field');
    });
    document.querySelectorAll('.field-error').forEach(el => el.remove());

    // 6. Очистка карт
    ['coord-n', 'coord-e', 'observ-coord-n', 'observ-coord-e'].forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.value = '';
            el.dispatchEvent(new Event('change', { bubbles: true }));
        }
    });

    // 7. Очистка полей ввода точки наблюдения (внутри таблицы add_observation_point)
    const observationInputIds = ["observ-point", "observ-coord-n", "observ-coord-e", "eco-type", "description"];
    observationInputIds.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.value = '';
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
