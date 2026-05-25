(function () {
    if (window.__reportNotificationsInitialized) {
        return;
    }
    window.__reportNotificationsInitialized = true;

    // Функция уведомлений отключена - отчет будет выделен на странице документов
    // Подключение к EventSource отключено
    // Оставляем пустую инициализацию для совместимости
})();
