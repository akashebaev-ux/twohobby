document.addEventListener("DOMContentLoaded", () => {
    const mapElement = document.getElementById("client-ride-map");

    if (!mapElement || typeof L === "undefined") {
        return;
    }

    const tileUrl = mapElement.dataset.tileUrl;
    const tileAttribution = mapElement.dataset.tileAttribution;

    if (!tileUrl) {
        console.error("Client ride map tile URL is missing.");
        return;
    }

    const almatyCoordinates = [43.238949, 76.889709];

    const map = L.map("client-ride-map", {
        center: almatyCoordinates,
        zoom: 12,
        zoomControl: true,
    });

    L.tileLayer(tileUrl, {
        attribution: tileAttribution || "",
        maxZoom: 19,
    }).addTo(map);

    L.control.scale({
        imperial: false,
        position: "bottomright",
    }).addTo(map);
});
