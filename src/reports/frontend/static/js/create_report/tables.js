window.addEventListener("DOMContentLoaded", function () {
    const addTable = document.getElementById("add_observation_point");
    const targetTable = document.getElementById("observation_points_table");

    if (!addTable || !targetTable) return;

    const addButton = addTable.closest("section")?.querySelector(".action__button");
    if (!addButton) return;

    addButton.addEventListener("click", function (event) {
        event.preventDefault();

        const values = [
            document.getElementById("observ-point")?.value.trim() || "",
            document.getElementById("observ-coord-n")?.value.trim() || "",
            document.getElementById("observ-coord-e")?.value.trim() || "",
            document.getElementById("eco-type")?.value.trim() || "",
            document.getElementById("description")?.value.trim() || "",
        ];

        const hasValue = values.some((value) => value.length > 0);
        if (!hasValue) return;

        const tbody = targetTable.querySelector("tbody");
        if (!tbody) return;  // Дополнительная проверка
        
        const rowCount = tbody.querySelectorAll("tr").length + 1;
        const row = document.createElement("tr");

        // Добавлить номер ряда
        const numCell = document.createElement("td");
        numCell.textContent = rowCount;
        row.appendChild(numCell);

        values.forEach((value) => {
            const cell = document.createElement("td");
            cell.textContent = value || "-";
            row.appendChild(cell);
        });

        tbody.appendChild(row);

        values.forEach((_, index) => {
            const inputIds = ["observ-point", "observ-coord-n", "observ-coord-e", "eco-type", "description"];
            const input = document.getElementById(inputIds[index]);
            if (input) input.value = "";
        });
    });
});

window.addEventListener("DOMContentLoaded", function () {
    const dynamicsTable = document.getElementById("observation_dynamics_table");
    if (!dynamicsTable) return;

    const dynamicsSection = dynamicsTable.closest("section");
    if (!dynamicsSection) return;

    const resultButtons = Array.from(dynamicsSection.querySelectorAll(".list_element"));
    if (resultButtons.length === 0) return;

    const addDateButton = dynamicsSection.querySelector(".section__row--small .action__button");
    if (!addDateButton) return;

    const tbody = dynamicsTable.querySelector("tbody") || dynamicsTable.appendChild(document.createElement("tbody"));
    const thead = dynamicsTable.querySelector("thead") || dynamicsTable.insertBefore(document.createElement("thead"), tbody);

    resultButtons.forEach((button) => {
        if (!button.dataset.selected) {
            button.dataset.selected = "true";
        }
        button.classList.toggle("list_element--active", button.dataset.selected === "true");
    });

    function getSelectedLabels() {
        return resultButtons
            .filter((button) => button.dataset.selected === "true")
            .map((button) => button.textContent.trim())
            .filter((label) => label.length > 0);
    }

    function readRowData(row) {
        const data = {};
        const inputs = row.querySelectorAll("input[data-field]");
        inputs.forEach((input) => {
            data[input.dataset.field] = input.value;
        });
        return data;
    }

    function buildRow(labelList, data) {
        const row = document.createElement("tr");

        labelList.forEach((label) => {
            const cell = document.createElement("td");
            const input = document.createElement("input");

            input.type = label === "Дата" ? "date" : "text";
            input.value = data[label] || "";
            input.dataset.field = label;

            cell.appendChild(input);
            row.appendChild(cell);
        });

        return row;
    }

    function renderTable() {
        const selectedLabels = getSelectedLabels();
        const labels = ["Дата", ...selectedLabels];
        const existingRows = Array.from(tbody.querySelectorAll("tr")).map(readRowData);

        thead.innerHTML = "";
        const headerRow = document.createElement("tr");
        labels.forEach((label) => {
            const th = document.createElement("th");
            th.textContent = label;
            headerRow.appendChild(th);
        });
        thead.appendChild(headerRow);

        tbody.innerHTML = "";
        existingRows.forEach((rowData) => {
            tbody.appendChild(buildRow(labels, rowData));
        });
    }

    resultButtons.forEach((button) => {
        button.addEventListener("click", function () {
            const isSelected = button.dataset.selected === "true";
            button.dataset.selected = isSelected ? "false" : "true";
            button.classList.toggle("list_element--active", !isSelected);
            renderTable();
        });
    });

    addDateButton.addEventListener("click", function (event) {
        event.preventDefault();
        const labels = ["Дата", ...getSelectedLabels()];
        tbody.appendChild(buildRow(labels, {}));
    });

    renderTable();
});

window.addEventListener("DOMContentLoaded", function () {
    const resultsTable = document.getElementById("test_results_table");
    if (!resultsTable) return;

    const resultsSection = resultsTable.closest("section");
    if (!resultsSection) return;

    const resultButtons = Array.from(resultsSection.querySelectorAll(".list_element"));
    if (resultButtons.length === 0) return;

    const tbody = resultsTable.querySelector("tbody") || resultsTable.appendChild(document.createElement("tbody"));

    // Нормативы для сравнения
    const standards = {
        "pH": { min: 6.00, max: 9.00, unit: "-" },
        "Железо": { min: 0.27, max: 0.33, unit: "мг/л" },
        "Марганец": { min: 0.085, max: 0.115, unit: "мг/л" },
        "Нитраты": { min: 38.25, max: 51.75, unit: "мг/л" },
        "Сульфаты": { min: 435.00, max: 565.00, unit: "мг/л" }
    };

    resultButtons.forEach((button) => {
        if (!button.dataset.selected) {
            button.dataset.selected = "true";
        }
        button.classList.toggle("list_element--active", button.dataset.selected === "true");
    });

    function getSelectedLabels() {
        return resultButtons
            .filter((button) => button.dataset.selected === "true")
            .map((button) => button.textContent.trim())
            .filter((label) => label.length > 0);
    }

    function readRowData() {
        const rows = Array.from(tbody.querySelectorAll("tr"));
        const data = new Map();

        rows.forEach((row) => {
            const indicator = row.dataset.indicator || "";
            if (!indicator) return;

            const inputs = row.querySelectorAll("input[data-field]");
            const rowData = {};
            inputs.forEach((input) => {
                rowData[input.dataset.field] = input.value;
            });

            data.set(indicator, rowData);
        });

        return data;
    }

    function compareWithStandard(indicator, resultValue) {
        const std = standards[indicator];
        if (!std) return "нет данных";
        
        const result = parseFloat(resultValue);
        if (isNaN(result)) return "";
        
        // Все показатели теперь имеют диапазон (min/max)
        if (std.min !== undefined && std.max !== undefined) {
            return result >= std.min && result <= std.max ? "да" : "нет";
        }
        return "";
    }

    function buildRow(indicator, data) {
        const row = document.createElement("tr");
        row.dataset.indicator = indicator;

        const indicatorCell = document.createElement("td");
        indicatorCell.textContent = indicator;
        row.appendChild(indicatorCell);

        const std = standards[indicator];
        
        // Норматив
        const standardCell = document.createElement("td");
        const standardInput = document.createElement("input");

        standardInput.type = "text";
        standardInput.readOnly = true;
        standardInput.dataset.field = "Норматив";

        if (std) {
            const min = std.min.toFixed(2);
            const max = std.max.toFixed(2);
            standardInput.value = `${min} - ${max}`;
        } else {
            standardInput.value = "";
        }

        standardCell.appendChild(standardInput);
        row.appendChild(standardCell);

        // Результат
        const resultCell = document.createElement("td");
        const resultInput = document.createElement("input");
        resultInput.type = "text";
        resultInput.value = data?.["Результат"] || "";
        resultInput.dataset.field = "Результат";
        resultInput.addEventListener("change", updateCompliance);
        resultCell.appendChild(resultInput);
        row.appendChild(resultCell);

        // Единицы измерения
        const unitCell = document.createElement("td");
        const unitInput = document.createElement("input");
        unitInput.type = "text";
        unitInput.value = std ? std.unit : "мг/л";
        unitInput.dataset.field = "Единицы измерения";
        unitInput.readOnly = true;
        unitCell.appendChild(unitInput);
        row.appendChild(unitCell);

        // Соответствие
        const complianceCell = document.createElement("td");
        const complianceInput = document.createElement("input");
        complianceInput.type = "text";
        complianceInput.value = data?.["Соответствие"] || compareWithStandard(indicator, data?.["Результат"] || "");
        complianceInput.dataset.field = "Соответствие";
        complianceInput.readOnly = true;
        complianceCell.appendChild(complianceInput);
        row.appendChild(complianceCell);

        function updateCompliance() {
            const resultValue = resultInput.value;
            complianceInput.value = compareWithStandard(indicator, resultValue);
        }

        return row;
    }

    function renderTable() {
        const selectedLabels = getSelectedLabels();
        const existingData = readRowData();
        tbody.innerHTML = "";

        selectedLabels.forEach((label) => {
            const rowData = existingData.get(label) || {};
            tbody.appendChild(buildRow(label, rowData));
        });
    }

    resultButtons.forEach((button) => {
        button.addEventListener("click", function () {
            const isSelected = button.dataset.selected === "true";
            button.dataset.selected = isSelected ? "false" : "true";
            button.classList.toggle("list_element--active", !isSelected);
            renderTable();
        });
    });

    renderTable();
});