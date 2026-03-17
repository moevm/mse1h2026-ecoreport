window.addEventListener("DOMContentLoaded", function () {
    const mapContainer = document.getElementById("coordinates-map");
    const coordNInput = document.getElementById("coord-n");
    const coordEInput = document.getElementById("coord-e");

    if (!mapContainer || !coordNInput || !coordEInput || typeof L === "undefined") {
        return;
    }

    const map = L.map("coordinates-map", {
        center: [55.751244, 37.618423],
        zoom: 5,
        zoomControl: true,
    });

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    }).addTo(map);

    let clickMarker = null;

    map.on("click", function (event) {
        const lat = Number(event.latlng.lat).toFixed(6);
        const lng = Number(event.latlng.lng).toFixed(6);

        coordNInput.value = lat;
        coordEInput.value = lng;

        if (clickMarker) {
            clickMarker.setLatLng(event.latlng);
            return;
        }

        clickMarker = L.circleMarker(event.latlng, {
            radius: 7,
            color: "#2A4D88",
            fillColor: "#7C94B8",
            fillOpacity: 0.9,
            weight: 2,
        }).addTo(map);
    });

    setTimeout(function () {
        map.invalidateSize();
    }, 100);
});
