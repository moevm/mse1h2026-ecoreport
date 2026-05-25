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
        GROUNDWATER_LEVEL: document.getElementById("groundwater-level")?.value.trim().replace(',', '.') || null,
        CLIMATE_ZONE: document.getElementById("climate-zone")?.value || "Умеренный",

        // координаты объекта
        COORDINATES_LATITUDE: parseFloat(document.getElementById("coord-n")?.value) || 55.75,
        COORDINATES_LONGITUDE: parseFloat(document.getElementById("coord-e")?.value) || 37.61,

        // характеристика системы
        OBJECT_TYPE: document.getElementById("object-type")?.value || "город",
        SYSTEM_TYPE: document.getElementById("type-system")?.value || "",
        PIPE_MATERIAL: document.getElementById("pipe-material")?.value.trim() || "",
        PIPE_DIAMETER: document.getElementById("pipe-diameter")?.value.trim().replace(',', '.') || null,
        PIPE_DEPTH: document.getElementById("burial-depth")?.value.trim().replace(',', '.') || null,
        PIPE_LENGTH: document.getElementById("total-length")?.value.trim().replace(',', '.') || null,
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

    const draftFileId = document.getElementById("draft-file-id")?.value;
    if (draftFileId) {
        data.file_id = parseInt(draftFileId);
    }

    try {
        const response = await fetch("/generate-report", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (result.status === "success") {
            // Сохраняем report_id в sessionStorage для выделения на странице документов
            sessionStorage.setItem("newReportId", result.report_id);
            
            // Удаляем все существующие toast-уведомления
            const toastContainer = document.querySelector(".report-toast-container");
            if (toastContainer) {
                toastContainer.innerHTML = "";
            }
            
            // Обновляем статус
            if (status) status.innerText = "Отчет генерируется. Переход на страницу отчетов...";
            
            // Переходим на страницу отчетов
            setTimeout(() => {
                window.location.href = "/documents";
            }, 500);
        } else {
            console.log(result.message);
        }
    } catch (error) {
        showToast("Ошибка соединения: " + error.message, "error");
    }
}

function collectDraftData() {
    return {
        FULL_OBJECT_NAME: document.getElementById("full-object-name")?.value || null,
        SHORT_OBJECT_NAME: document.getElementById("short-object-name")?.value || null,
        YEAR: parseInt(document.getElementById("report-year")?.value) || null,
        ORGANIZATION_NAME: document.getElementById("organization-name")?.value || null,
        REGION: document.getElementById("region")?.value || null,
        DOCUMENTS_GOST: JSON.parse(localStorage.getItem("gost_list") || "[]"),
        RELIEF_TYPE: document.getElementById("relief-type")?.value || null,
        SOIL_TYPE: document.getElementById("soil-type")?.value || null,
        GROUNDWATER_LEVEL: document.getElementById("groundwater-level")?.value?.trim()?.replace(",", ".") || null,
        CLIMATE_ZONE: document.getElementById("climate-zone")?.value || null,
        COORDINATES_LATITUDE: parseFloat(document.getElementById("coord-n")?.value) || null,
        COORDINATES_LONGITUDE: parseFloat(document.getElementById("coord-e")?.value) || null,
        OBJECT_TYPE: document.getElementById("object-type")?.value || null,
        SYSTEM_TYPE: document.getElementById("type-system")?.value || null,
        PIPE_MATERIAL: document.getElementById("pipe-material")?.value?.trim() || null,
        PIPE_DIAMETER: document.getElementById("pipe-diameter")?.value?.trim()?.replace(",", ".") || null,
        PIPE_DEPTH: document.getElementById("burial-depth")?.value?.trim()?.replace(",", ".") || null,
        PIPE_LENGTH: document.getElementById("total-length")?.value?.trim()?.replace(",", ".") || null,
        PIPE_INSTALL_YEAR: parseInt(document.getElementById("laying-year")?.value) || null,
        MANHOLE_COUNT: parseInt(document.getElementById("wells-count")?.value) || null,
        MONITORING_POINT_COUNT: parseInt(document.getElementById("monitor-amount")?.value) || null,
        OBSERVATION_POINT: document.getElementById("observ-point")?.value || null,
        LATITUDE: parseFloat(document.getElementById("observ-coord-n")?.value) || null,
        LONGITUDE: parseFloat(document.getElementById("observ-coord-e")?.value) || null,
        MEDIUM_TYPE: document.getElementById("eco-type")?.value || null,
        DESCRIPTION: document.getElementById("description")?.value || null,
        OBSERVATION_FREQUENCY: document.getElementById("observ-period")?.value || null,
        OBSERVATION_POINTS: readObservationPoints(),
        ...(() => {
            const indicatorToField = { "pH": "RESULTS_PH", "Железо": "RESULTS_IRON", "Марганец": "RESULTS_MANGANESE", "Нитраты": "RESULTS_NITRATES", "Сульфаты": "RESULTS_SULFATES" };
            const map = { RESULTS_PH: null, RESULTS_IRON: null, RESULTS_MANGANESE: null, RESULTS_NITRATES: null, RESULTS_SULFATES: null };
            readTestResults().forEach((r) => {
                const field = indicatorToField[r.indicator];
                if (field !== undefined) map[field] = r.result;
            });
            return map;
        })(),
        TEST_RESULTS: readTestResults(),
        RESULTS_DYNAMIC: [],
        OBSERVATION_DYNAMICS: readObservationDynamics(),
        ORGANIZATION_ADDRESS: document.getElementById("org-address")?.value || null,
        ORGANIZATION_PHONE: document.getElementById("org-phone")?.value || null,
        ORGANIZATION_EMAIL: document.getElementById("org-email")?.value || null,
        RESPONSIBLE_NAME: document.getElementById("resp-name")?.value || null,
        RESPONSIBLE_POSITION: document.getElementById("resp-pos")?.value || null,
        REPORT_DATE: document.getElementById("report-date")?.value || null,
        SELECTED_TEST_INDICATORS: (function () {
            const section = document.getElementById("test_results_table")?.closest("section");
            if (!section) return null;
            return Array.from(section.querySelectorAll(".list_element"))
                .filter((btn) => btn.dataset.selected !== "false")
                .map((btn) => btn.textContent.trim());
        })(),
    };
}

async function saveDraft() {
    const data = collectDraftData();

    if (!data.ORGANIZATION_NAME || !data.ORGANIZATION_NAME.trim()) {
        const el = document.getElementById("organization-name");
        highlightError(el);
        el?.focus();
        showToast("Укажите название организации", "error");
        return;
    }
    if (!data.FULL_OBJECT_NAME || !data.FULL_OBJECT_NAME.trim()) {
        const el = document.getElementById("full-object-name");
        highlightError(el);
        el?.focus();
        showToast("Укажите полное название объекта", "error");
        return;
    }

    const draftFileId = document.getElementById("draft-file-id")?.value;
    if (draftFileId) {
        data.file_id = parseInt(draftFileId);
    }

    try {
        const response = await fetch("/save-draft", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data),
        });
        if (!response.ok) {
            const err = await response.json().catch(() => ({}));
            showToast("Ошибка при сохранении черновика: " + (err.detail || response.status), "error");
            return;
        }
        const result = await response.json();
        const hiddenInput = document.getElementById("draft-file-id");
        if (hiddenInput) hiddenInput.value = result.file_id;
        showToast("Черновик сохранён", "success");
    } catch (error) {
        showToast("Ошибка соединения: " + error.message, "error");
    }
}

async function deleteDraft() {
    const draftFileId = document.getElementById("draft-file-id")?.value;
    if (!draftFileId) {
        showToast("Сначала сохраните черновик", "info");
        return;
    }
    if (!confirm("Удалить черновик?")) return;

    try {
        const response = await fetch(`/delete-draft/${draftFileId}`, { method: "DELETE" });
        if (!response.ok && response.status !== 204) {
            const err = await response.json().catch(() => ({}));
            showToast("Ошибка: " + (err.detail || response.status), "error");
            return;
        }
        document.getElementById("draft-file-id").value = "";
        clearForm();
        showToast("Черновик удалён", "success");
    } catch (error) {
        showToast("Ошибка соединения: " + error.message, "error");
    }
}

async function prefillFromDraft() {
    const params = new URLSearchParams(window.location.search);
    const draftId = params.get("draft_id");
    if (!draftId) return;

    try {
        const response = await fetch(`/draft/${draftId}`);
        if (!response.ok) return;
        const d = await response.json();

        const set = (id, val) => {
            const el = document.getElementById(id);
            if (el && val !== null && val !== undefined) el.value = val;
        };

        set("full-object-name", d.FULL_OBJECT_NAME);
        set("short-object-name", d.SHORT_OBJECT_NAME);
        set("report-year", d.YEAR);
        set("organization-name", d.ORGANIZATION_NAME);
        set("region", d.REGION);
        set("relief-type", d.RELIEF_TYPE);
        set("soil-type", d.SOIL_TYPE);
        set("groundwater-level", d.GROUNDWATER_LEVEL);
        set("climate-zone", d.CLIMATE_ZONE);
        set("coord-n", d.COORDINATES_LATITUDE);
        set("coord-e", d.COORDINATES_LONGITUDE);
        set("object-type", d.OBJECT_TYPE);
        set("type-system", d.SYSTEM_TYPE);
        set("pipe-material", d.PIPE_MATERIAL);
        set("pipe-diameter", d.PIPE_DIAMETER);
        set("burial-depth", d.PIPE_DEPTH);
        set("total-length", d.PIPE_LENGTH);
        set("laying-year", d.PIPE_INSTALL_YEAR);
        set("wells-count", d.MANHOLE_COUNT);
        set("monitor-amount", d.MONITORING_POINT_COUNT);
        set("observ-point", d.OBSERVATION_POINT);
        set("observ-coord-n", d.LATITUDE);
        set("observ-coord-e", d.LONGITUDE);
        set("eco-type", d.MEDIUM_TYPE);
        set("description", d.DESCRIPTION);
        set("observ-period", d.OBSERVATION_FREQUENCY);
        set("org-address", d.ORGANIZATION_ADDRESS);
        set("org-phone", d.ORGANIZATION_PHONE);
        set("org-email", d.ORGANIZATION_EMAIL);
        set("resp-name", d.RESPONSIBLE_NAME);
        set("resp-pos", d.RESPONSIBLE_POSITION);
        set("report-date", d.REPORT_DATE);

        if (d.DOCUMENTS_GOST && d.DOCUMENTS_GOST.length) {
            localStorage.setItem("gost_list", JSON.stringify(d.DOCUMENTS_GOST));
            const knownGosts = new Set(Array.from(document.querySelectorAll("#gost_list .list_element")).map((b) => b.textContent.trim()));
            const customGost = d.DOCUMENTS_GOST.find((g) => !knownGosts.has(g)) || "";
            if (customGost) {
                localStorage.setItem("gost_other", customGost);
                const otherInput = document.getElementById("gost-other");
                if (otherInput) otherInput.value = customGost;
            }
        }

        if (d.SELECTED_TEST_INDICATORS && window.restoreTestResults) {
            const fmt = (v) => (v !== null && v !== undefined) ? Number(v).toFixed(2) : undefined;
            const valuesMap = {};
            const ph = fmt(d.RESULTS_PH); if (ph !== undefined) valuesMap["pH"] = ph;
            const iron = fmt(d.RESULTS_IRON); if (iron !== undefined) valuesMap["Железо"] = iron;
            const mn = fmt(d.RESULTS_MANGANESE); if (mn !== undefined) valuesMap["Марганец"] = mn;
            const no3 = fmt(d.RESULTS_NITRATES); if (no3 !== undefined) valuesMap["Нитраты"] = no3;
            const so4 = fmt(d.RESULTS_SULFATES); if (so4 !== undefined) valuesMap["Сульфаты"] = so4;
            window.restoreTestResults(d.SELECTED_TEST_INDICATORS, valuesMap);
        }

        if (d.OBSERVATION_POINTS && d.OBSERVATION_POINTS.length > 0 && window.restoreObservationPoints) {
            window.restoreObservationPoints(d.OBSERVATION_POINTS);
        }

        if (d.OBSERVATION_DYNAMICS && d.OBSERVATION_DYNAMICS.length > 0 && window.restoreDynamics) {
            window.restoreDynamics(d.OBSERVATION_DYNAMICS);
        }

        const hiddenInput = document.getElementById("draft-file-id");
        if (hiddenInput) hiddenInput.value = d.file_id;
    } catch (e) {
        console.error("Ошибка загрузки черновика:", e);
    }
}

document.addEventListener("DOMContentLoaded", () => {
    prefillFromDraft();
});