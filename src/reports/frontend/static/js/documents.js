(function () {

    function highlightNewReport() {
        const newReportId = sessionStorage.getItem("newReportId");

        if (!newReportId) {
            return;
        }

        const cards = document.querySelectorAll("[data-report-id]");
        let found = false;

        cards.forEach(card => {
            if (card.dataset.reportId === newReportId) {

                // Базовое выделение
                card.classList.add("card--new-report");

                // Одноразовая анимация
                card.classList.add("animate");

                found = true;

                // Скролл к карточке
                setTimeout(() => {
                    card.scrollIntoView({
                        behavior: "smooth",
                        block: "center"
                    });
                }, 150);

                // Убираем класс анимации после завершения
                card.addEventListener("animationend", () => {
                    card.classList.remove("animate");
                }, { once: true });
            }
        });

        if (found) {
            // Удаляем ID, чтобы больше не анимировать
            sessionStorage.removeItem("newReportId");
        } else {
            // Повторная попытка если отчет еще не появился
            setTimeout(highlightNewReport, 1000);
        }
    }

    if (document.readyState === "loading") {
        document.addEventListener(
            "DOMContentLoaded",
            highlightNewReport
        );
    } else {
        highlightNewReport();
    }

})();