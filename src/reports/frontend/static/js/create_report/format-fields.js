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