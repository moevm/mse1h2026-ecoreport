document.addEventListener("DOMContentLoaded", () => {
    const registerForm = document.querySelector("[data-register-form]");
    const loginForm = document.querySelector("[data-login-form]");

    const submitAuthForm = async ({ form, successUrl, payload, failureMessage }) => {
        const submitButton = form.querySelector(".auth-card__submit");
        const previousLabel = submitButton?.textContent ?? "";

        try {
            if (submitButton) {
                submitButton.disabled = true;
            }

            const response = await fetch(form.action, {
                method: "POST",
                credentials: "same-origin",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(payload),
            });

            if (!response.ok) {
                showToast(failureMessage, "error");
                return;
            }

            window.location.assign(successUrl);
        } catch (error) {
            showToast(failureMessage, "error");
        } finally {
            if (submitButton) {
                submitButton.disabled = false;
                submitButton.textContent = previousLabel;
            }
        }
    };

    function validateFields(form) {
        const usernameInput = form.querySelector("#username");
        const passwordInput = form.querySelector("#password");
        let valid = true;

        if (!usernameInput.value.trim()) {
            highlightError(usernameInput);
            valid = false;
        }
        if (!passwordInput.value) {
            highlightError(passwordInput);
            valid = false;
        }
        if (!valid) {
            showToast("Заполните все поля.", "error");
        }
        return valid;
    }

    if (registerForm) {
        registerForm.addEventListener("submit", async (event) => {
            event.preventDefault();

            const userName = registerForm.querySelector("#username").value.trim();
            const password = registerForm.querySelector("#password").value;

            if (!validateFields(registerForm)) return;

            await submitAuthForm({
                form: registerForm,
                successUrl: registerForm.dataset.loginUrl || "/login",
                payload: {
                    user_name: userName,
                    password,
                },
                failureMessage: "Ошибка при создании пользователя.",
            });
        });
    }

    if (loginForm) {
        loginForm.addEventListener("submit", async (event) => {
            event.preventDefault();

            const userName = loginForm.querySelector("#username").value.trim();
            const password = loginForm.querySelector("#password").value;

            if (!validateFields(loginForm)) return;

            await submitAuthForm({
                form: loginForm,
                successUrl: loginForm.dataset.appUrl || "/",
                payload: {
                    user_name: userName,
                    password,
                },
                failureMessage: "Неверное имя пользователя или пароль.",
            });
        });
    }
});
