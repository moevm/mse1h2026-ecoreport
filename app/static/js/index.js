async function uploadFile() {
    const fileInput = document.getElementById("file-input");
    const status = document.getElementById("upload-status");

    if (!fileInput.files.length) {
        status.innerText = "Выберите файл!";
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    status.innerText = "Загрузка...";

    try {
        const response = await fetch("/upload/", {
            method: "POST",
            body: formData
        });

        const result = await response.json();

        if (result.status === "success") {
            status.innerText = "Файл успешно загружен";
            console.log(result.saved_as);

        } else {
            status.innerText = "Ошибка: " + result.message;
        }

    } catch (error) {
        status.innerText = "Ошибка соединения";
    }
}

async function sendForm() {
    const form = document.getElementById("input-form");
    const formData = new FormData(form);
    const status = document.getElementById("report-status");

    try {
        const response = await fetch("/generate-report", {
            method: "POST",
            body: formData
        });

        const result = await response.json();

        if (result.status === "success") {
            status.innerText = "Отчет готов!";
        } else {
            status.innerText = "Ошибка: " + result.message;
        }
    } catch (error) {
        status.innerText = "Ошибка соединения";
    }
}