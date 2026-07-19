document.addEventListener("DOMContentLoaded", () => {
    const mapElement = document.getElementById(
        "ride-tracking-map"
    );

    const mapDataElement = document.getElementById(
        "ride-tracking-map-data"
    );

    if (!mapElement || !mapDataElement) {
        return;
    }

    const mapData = JSON.parse(mapDataElement.textContent);

    const startCoordinates = [
        mapData.start_latitude,
        mapData.start_longitude,
    ];

    const destinationCoordinates = [
        mapData.destination_latitude,
        mapData.destination_longitude,
    ];

    const map = L.map("ride-tracking-map", {
        zoomControl: false,
    });

    L.tileLayer(mapElement.dataset.tileUrl, {
        attribution: mapElement.dataset.tileAttribution,
        maxZoom: 19,
    }).addTo(map);

    L.control.zoom({
        position: "topright",
    }).addTo(map);

    const pickupIcon = L.divIcon({
        className: "tracking-marker-wrapper",
        html: `
            <span class="tracking-marker tracking-marker-pickup"></span>
        `,
        iconSize: [24, 24],
        iconAnchor: [12, 12],
    });

    const destinationIcon = L.divIcon({
        className: "tracking-marker-wrapper",
        html: `
            <span class="tracking-marker tracking-marker-destination"></span>
        `,
        iconSize: [24, 24],
        iconAnchor: [12, 12],
    });

    L.marker(startCoordinates, {
        icon: pickupIcon,
    })
        .addTo(map)
        .bindPopup(mapData.start_name);

    L.marker(destinationCoordinates, {
        icon: destinationIcon,
    })
        .addTo(map)
        .bindPopup(mapData.destination_name);

    const routeLine = L.polyline(
        [
            startCoordinates,
            destinationCoordinates,
        ],
        {
            color: "#111111",
            weight: 6,
            opacity: 1,
        }
    ).addTo(map);

    map.fitBounds(routeLine.getBounds(), {
        padding: [50, 50],
    });
});
