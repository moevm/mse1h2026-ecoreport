document.addEventListener("DOMContentLoaded", () => {
    const userMenu = document.querySelector(".topbar__user-menu");
    if (!userMenu) {
        return;
    }

    const toggleButton = userMenu.querySelector(".topbar__avatar-button");
    const dropdown = userMenu.querySelector(".topbar__dropdown");

    if (!toggleButton || !dropdown) {
        return;
    }

    const closeMenu = () => {
        dropdown.hidden = true;
        toggleButton.setAttribute("aria-expanded", "false");
    };

    const openMenu = () => {
        dropdown.hidden = false;
        toggleButton.setAttribute("aria-expanded", "true");
    };

    toggleButton.addEventListener("click", (event) => {
        event.stopPropagation();

        if (dropdown.hidden) {
            openMenu();
            return;
        }

        closeMenu();
    });

    document.addEventListener("click", (event) => {
        if (!userMenu.contains(event.target)) {
            closeMenu();
        }
    });

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            closeMenu();
        }
    });
});
