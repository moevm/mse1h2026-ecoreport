function initCoordinatesMap(config) {
    const mapEl = config.mapEl;
    const latInput = config.latInput;
    const lngInput = config.lngInput;

    if (!mapEl || !latInput || !lngInput || typeof L === "undefined") {
        return null;
    }

    const center = config.center || [55.75, 37.61];
    const zoom = config.zoom || 5;
    const tileUrl = config.tileUrl;
    const attribution = config.attribution;

    const map = L.map(mapEl, {
        center: center,
        zoom: zoom,
        zoomControl: true,
    });

    L.tileLayer(tileUrl, {
        maxZoom: 19,
        attribution: attribution,
    }).addTo(map);

    let marker = null;

    marker = L.circleMarker([config.latInput.value, config.lngInput.value], {
        radius: 5,
        color: "#2A4D88",
        fillColor: "#7C94B8",
        weight: 2,
    }).addTo(map);

    document.getElementById(config.latInput.id).addEventListener("change", function() {
        marker.setLatLng([config.latInput.value, config.lngInput.value])
    });

    document.getElementById(config.lngInput.id).addEventListener("change", function() {
        marker.setLatLng([config.latInput.value, config.lngInput.value])
    });

    map.on("click", function (event) {
        latInput.value = Number(event.latlng.lat).toFixed(6);
        lngInput.value = Number(event.latlng.lng).toFixed(6);
        marker.setLatLng(event.latlng);
    });

    return map;
}

window.addEventListener("DOMContentLoaded", function () {
    function mountMap(mapId, latId, lngId) {
        const mapContainer = document.getElementById(mapId);
        const coordNInput = document.getElementById(latId);
        const coordEInput = document.getElementById(lngId);

        if (!mapContainer || !coordNInput || !coordEInput) {
            return null;
        }

        return initCoordinatesMap({
            mapEl: mapContainer,
            latInput: coordNInput,
            lngInput: coordEInput,
            center: [55.751244, 37.618423],
            zoom: 5,
            tileUrl: mapContainer.dataset.osmTileUrl,
            attribution: mapContainer.dataset.osmAttribution,
        });
    }

    mountMap("coordinates-map", "coord-n", "coord-e");
    mountMap("observ-coordinates-map", "observ-coord-n", "observ-coord-e");
});