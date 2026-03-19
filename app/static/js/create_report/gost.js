window.addEventListener("DOMContentLoaded", function () {
	const gostList = document.getElementById("gost_list");
	if (!gostList) return;

	const buttons = Array.from(gostList.querySelectorAll(".list_element"));
	if (buttons.length === 0) return;

	let gost_list = localStorage.getItem("gost_list") ?
		new Set(JSON.parse(localStorage.getItem("gost_list"))) : new Set([]);

	buttons.forEach((button) => {
		if (gost_list.has(button.textContent)) button.classList.add("list_element--active");

		button.addEventListener("click", function () {
			const label = button.textContent.trim();
			const isActive = button.classList.toggle("list_element--active");

			if (label) {
				if (isActive) gost_list.add(label)
				else gost_list.delete(label)
			}

            localStorage.setItem("gost_list", JSON.stringify([...gost_list]));
		});
	});
});
