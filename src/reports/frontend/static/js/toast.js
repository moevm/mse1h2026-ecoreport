(function () {
    const DURATION = 4000;

    function ensureContainer() {
        let c = document.getElementById("toast-container");
        if (!c) {
            c = document.createElement("div");
            c.id = "toast-container";
            document.body.appendChild(c);
        }
        return c;
    }

    window.showToast = function (message, type) {
        // type: "success" | "error" | "info"
        const container = ensureContainer();
        const toast = document.createElement("div");
        toast.className = "toast toast--" + (type || "info");

        const icon = document.createElement("span");
        icon.className = "toast__icon";
        icon.textContent = type === "success" ? "✓" : type === "error" ? "✕" : "ℹ";

        const text = document.createElement("span");
        text.className = "toast__text";
        text.textContent = message;

        const close = document.createElement("button");
        close.className = "toast__close";
        close.textContent = "×";
        close.addEventListener("click", () => dismiss(toast));

        toast.appendChild(icon);
        toast.appendChild(text);
        toast.appendChild(close);
        container.appendChild(toast);

        requestAnimationFrame(() => toast.classList.add("toast--visible"));

        const timer = setTimeout(() => dismiss(toast), DURATION);
        toast._timer = timer;
    };

    function dismiss(toast) {
        clearTimeout(toast._timer);
        toast.classList.remove("toast--visible");
        toast.classList.add("toast--hiding");
        toast.addEventListener("transitionend", () => toast.remove(), { once: true });
    }

    window.highlightError = function (inputEl) {
        if (!inputEl) return;
        inputEl.classList.add("input--error");
        inputEl.addEventListener(
            "input",
            () => inputEl.classList.remove("input--error"),
            { once: true }
        );
    };
})();
