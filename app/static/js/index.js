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

window.addEventListener('load', function () {
    const site_type_input = document.getElementById("site-type");
    const bog_extra = document.getElementById("bog-extra");
    const urban_extra = document.getElementById("urban-extra");
    const protected_extra = document.getElementById("protected-extra");
    site_type_input.addEventListener('input', function() {
        bog_extra.hidden = true;
        urban_extra.hidden = true;
        protected_extra.hidden = true;
        switch (site_type_input.value){
            case "bog":
                bog_extra.hidden = false;
                break;
            case "urban":
                urban_extra.hidden = false;
                break;
            case "protected":
                protected_extra.hidden = false;
                break;
            default:
                break;
    
        }
    
    });
})
