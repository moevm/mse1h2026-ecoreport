(function () {
    if (window.__reportNotificationsInitialized) {
        return;
    }
    window.__reportNotificationsInitialized = true;

    function createContainer() {
        let container = document.querySelector(".report-toast-container");
        if (!container) {
            container = document.createElement("div");
            container.className = "report-toast-container";
            document.body.appendChild(container);
        }
        return container;
    }

    function removeToast(toast) {
        toast.classList.remove("report-toast--visible");
        toast.addEventListener(
            "transitionend",
            () => {
                toast.remove();
            },
            { once: true }
        );
    }

    function makeLink(href, text) {
        const a = document.createElement("a");
        a.className = "report-toast__link";
        a.href = href;
        a.target = "_blank";
        a.rel = "noopener noreferrer";
        a.textContent = text+" ";
        return a;
    }

    function showReportReadyToast(eventData) {
        const container = createContainer();

        const toast = document.createElement("div");
        toast.className = "report-toast";

        const title = document.createElement("h4");
        title.className = "report-toast__title";
        title.textContent = eventData?.title || "Отчет готов";

        const closeBtn = document.createElement("button");
        closeBtn.className = "report-toast__close";
        closeBtn.type = "button";
        closeBtn.setAttribute("aria-label", "Закрыть уведомление");
        closeBtn.textContent = "Закрыть";

        toast.appendChild(title);

        if (eventData?.download_url) {
            toast.appendChild(makeLink(eventData.download_url, "Скачать отчет"));
        }

        if (eventData?.geojson_download_url) {
            toast.appendChild(makeLink(eventData.geojson_download_url, "Скачать GeoJSON"));
        }

        toast.appendChild(closeBtn);
        container.appendChild(toast);

        requestAnimationFrame(() => {
            toast.classList.add("report-toast--visible");
        });

        closeBtn.addEventListener("click", () => {
            removeToast(toast);
        });
    }

    function connectReportEvents() {
        const source = new EventSource("/events/report-ready");

        source.addEventListener("report_ready", (event) => {
            const payload = JSON.parse(event.data);
            showReportReadyToast(payload);
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", connectReportEvents, { once: true });
    } else {
        connectReportEvents();
    }
})();
