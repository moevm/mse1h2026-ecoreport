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

// функция для валидации даты (не в будущем)
function validateDateNotFuture(value) {
    if (!value) return false;
    const date = new Date(value);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    return !Number.isNaN(date.getTime()) && date <= today;
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