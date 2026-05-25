// функция для очистки всех полей на странице создания отчета
function clearAllFormFields() {
    console.log("Start clearing forms");

    // 1. Очищаем обычные поля ввода и select
    const regularFields = document.querySelectorAll(`
        input:not([type="button"]):not([type="submit"]):not([type="hidden"]),
        select
    `);

    // не трогаем поля внутри таблиц
    regularFields.forEach(field => {
        if (field.closest('table')) return;

        if (field.tagName === 'SELECT') {
            field.selectedIndex = 0;
        } else {
            field.value = '';
        }
    });


    // 2. Очистка таблиц
    // --------------------------
    // Таблица "Точки наблюдения"
    const pointsTbody = document.querySelector('#observation_points_table tbody');
    if (pointsTbody) {
        pointsTbody.innerHTML = '';
    }

    const testResultsTbody = document.querySelector('#test_results_table tbody');
    if (testResultsTbody) {
        const resultInputs = testResultsTbody.querySelectorAll('input[data-field="Результат"]');

        resultInputs.forEach(input => {
            const oldValue = input.value;
            input.value = '';

            // Обновляем поле "Соответствие" после очищения таблицы
            if (oldValue !== '') {
                const changeEvent = new Event('change', { bubbles: true });
                input.dispatchEvent(changeEvent);
            }
        });
    }

    // Таблица "Динамика наблюдений"
    const dynamicsTbody = document.querySelector('#observation_dynamics_table tbody');
    if (dynamicsTbody) {
        dynamicsTbody.innerHTML = '';
    }

    // 3. Сброс кнопок ГОСТов
    const gostButtons = document.querySelectorAll('#gost_list .list_element');
    gostButtons.forEach(btn => {
        btn.classList.remove('list_element--active');
        btn.dataset.selected = "false";
    });

    // 4. Сброс синих кнопок (pH, Железо, Марганец и т.д.)
    const toggleButtons = document.querySelectorAll('.list_element:not(#gost_list .list_element)');
    toggleButtons.forEach(button => {
        button.dataset.selected = "false";
        button.classList.add('list_element--active');
    });
    toggleButtons.forEach(button => button.click());

    // 5. Очистка ошибок валидации
    document.querySelectorAll('.invalid-field').forEach(el => {
        el.classList.remove('invalid-field');
    });
    document.querySelectorAll('.field-error').forEach(el => el.remove());

    // 6. Очистка карт
    ['coord-n', 'coord-e', 'observ-coord-n', 'observ-coord-e'].forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.value = '';
            el.dispatchEvent(new Event('change', { bubbles: true }));
        }
    });

    // 7. Очистка полей ввода точки наблюдения (внутри таблицы add_observation_point)
    const observationInputIds = ["observ-point", "observ-coord-n", "observ-coord-e", "eco-type", "description"];
    observationInputIds.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.value = '';
        }
    });
}

function clearForm() {
    const inputs = document.querySelectorAll("input:not([type=hidden]):not([type=file]), select, textarea");
    inputs.forEach((el) => {
        if (el.type === "checkbox" || el.type === "radio") {
            el.checked = false;
        } else {
            el.value = "";
        }
    });
    localStorage.removeItem("gost_list");
    localStorage.removeItem("gost_other");
    const tables = document.querySelectorAll(".dynamic-table tbody");
    tables.forEach((tbody) => { tbody.innerHTML = ""; });
}
