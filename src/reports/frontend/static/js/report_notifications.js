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

    function showReportReadyToast(eventData) {
        const container = createContainer();

        const toast = document.createElement("div");
        toast.className = "report-toast";

        const title = document.createElement("h4");
        title.className = "report-toast__title";
        title.textContent = eventData?.title || "Отчет готов";

        let fileType = eventData?.file_type ? eventData.file_type.toLowerCase().trim() : "";
        if (!fileType && eventData?.file_name) {
            const fileName = eventData.file_name.toLowerCase();
            if (fileName.endsWith(".docx") || fileName.endsWith(".doc")) {
                fileType = "docx";
            } else if (fileName.endsWith(".pdf")) {
                fileType = "pdf";
            }
        }
        if (!fileType && eventData?.download_url) {
            const url = eventData.download_url.toLowerCase();
            if (url.endsWith(".docx") || url.endsWith(".doc")) {
                fileType = "docx";
            } else if (url.endsWith(".pdf")) {
                fileType = "pdf";
            }
        }
        
        const downloadLink = document.createElement("a");
        downloadLink.className = "report-toast__link";
        downloadLink.href = eventData?.download_url || "#";
        downloadLink.target = "_blank";
        downloadLink.rel = "noopener noreferrer";
        
        console.log("Toast data:", {
            file_type: eventData?.file_type,
            file_name: eventData?.file_name,
            download_url: eventData?.download_url,
            detected_file_type: fileType
        });
        
        if (fileType === "docx" || fileType === "doc") {
            downloadLink.textContent = "Скачать отчет DOCX";
        } else if (fileType === "pdf") {
            downloadLink.textContent = "Скачать отчет PDF";
        } else {
            downloadLink.textContent = "Скачать отчет";
            console.warn("Unknown file type:", fileType, "Full data:", eventData);
        }

        const closeBtn = document.createElement("button");
        closeBtn.className = "report-toast__close";
        closeBtn.type = "button";
        closeBtn.setAttribute("aria-label", "Закрыть уведомление");
        closeBtn.textContent = "Закрыть";

        toast.appendChild(title);
        toast.appendChild(downloadLink);
        toast.appendChild(closeBtn);
        container.appendChild(toast);

        requestAnimationFrame(() => {
            toast.classList.add("report-toast--visible");
        });

        closeBtn.addEventListener("click", () => {
            removeToast(toast);
        });
    }

    let eventSource = null;
    let reconnectAttempts = 0;
    const MAX_RECONNECT_ATTEMPTS = 5;
    const BASE_RECONNECT_DELAY = 1000; 

    function connectReportEvents() {
        if (eventSource) {
            eventSource.removeEventListener("report_ready", handleReportReady);
            eventSource.close();
        }

        eventSource = new EventSource("/events/report-ready");
        eventSource.addEventListener("report_ready", handleReportReady);
        eventSource.onerror = function (event) {
            console.error("EventSource connection error:", event);
            eventSource.close();
            if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
                reconnectAttempts++;
                const delay = BASE_RECONNECT_DELAY * Math.pow(2, reconnectAttempts - 1);
                console.log(`Reconnecting in ${delay}ms (attempt ${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS})`);
                setTimeout(connectReportEvents, delay);
            } else {
                console.error("Max reconnection attempts reached. Giving up.");
            }
        };
        eventSource.onopen = function () {
            console.log("EventSource connected successfully");
            reconnectAttempts = 0;
        };
    }

    function handleReportReady(event) {
        try {
            const payload = JSON.parse(event.data);
            console.log("Received report ready event:", payload);
            showReportReadyToast(payload);
        } catch (e) {
            console.error("Failed to parse event data:", e, "Raw data:", event.data);
        }
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", connectReportEvents, { once: true });
    } else {
        connectReportEvents();
    }
})();
