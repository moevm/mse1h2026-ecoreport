async function uploadFile() {
    const fileInput = document.getElementById("file-input");
    const status = document.getElementById("status");

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
            const form = document.getElementById("manual-input");
            const input = document.getElementById('filename-input');
            input.value = result.saved_as;
            form.appendChild(input);
            console.log(result.saved_as);

        } else {
            status.innerText = "Ошибка: " + result.message;
        }

    } catch (error) {
        status.innerText = "Ошибка соединения";
    }
}