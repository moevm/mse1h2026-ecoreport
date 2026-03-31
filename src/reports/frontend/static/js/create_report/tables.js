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

        const tbody = targetTable.querySelector("tbody") || targetTable.appendChild(document.createElement("tbody"));
        const row = document.createElement("tr");

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

    function buildRow(indicator, data) {
        const row = document.createElement("tr");
        row.dataset.indicator = indicator;

        const indicatorCell = document.createElement("td");
        indicatorCell.textContent = indicator;
        row.appendChild(indicatorCell);

        const fields = [
            { key: "Норматив", value: data?.["Норматив"] || "" },
            { key: "Результат", value: data?.["Результат"] || "" },
            { key: "Единицы измерения", value: data?.["Единицы измерения"] || "мг/л" },
        ];

        fields.forEach((field) => {
            const cell = document.createElement("td");
            const input = document.createElement("input");
            input.type = "text";
            input.value = field.value;
            input.dataset.field = field.key;
            cell.appendChild(input);
            row.appendChild(cell);
        });

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