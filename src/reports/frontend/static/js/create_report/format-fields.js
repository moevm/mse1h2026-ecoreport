// Форматирует строку до положительного числа с двумя знаками после запятой.
// Возвращает отформатированную строку или null, если значение некорректно.
function formatTwoDecimals(value) {
    const normalized = value.trim().replace(",", ".");
    const num = parseFloat(normalized);
    if (isNaN(num) || num <= 0) return null;
    return num.toFixed(2);
}

// Применяет форматирование к полю ввода при потере фокуса.
// Если значение корректно обновляет поле и генерирует событие input,
// чтобы сработали существующие обработчики (валидация, обновление соответствия).
function applyTwoDecimalsFormat(input) {
    const val = input.value.trim();
    if (!val) return;
    const formatted = formatTwoDecimals(val);
    if (formatted !== null && formatted !== val) {
        input.value = formatted;
        input.dispatchEvent(new Event("input", { bubbles: true }));
    }
}

// Привязывает автоформатирование к статичному полю по его ID.
function attachFormatTwoDecimalsOnBlur(id) {
    const field = document.getElementById(id);
    if (!field) return;
    field.addEventListener("blur", function () {
        applyTwoDecimalsFormat(this);
    });
}

    // автоформатирование статичных числовых полей при потере фокуса
    attachFormatTwoDecimalsOnBlur("groundwater-level");
    attachFormatTwoDecimalsOnBlur("pipe-diameter");
    attachFormatTwoDecimalsOnBlur("total-length");
    attachFormatTwoDecimalsOnBlur("burial-depth");

    // автоформатирование числовых ячеек в динамических таблицах при потере фокуса
    document.addEventListener("focusout", function (event) {
        const target = event.target;
        if (!(target instanceof HTMLInputElement)) return;

        if (target.closest("#test_results_table") && target.dataset.field === "Результат") {
            applyTwoDecimalsFormat(target);
        }

        if (target.closest("#observation_dynamics_table") &&
            target.dataset.field && target.dataset.field !== "Дата") {
            applyTwoDecimalsFormat(target);
        }
    });
