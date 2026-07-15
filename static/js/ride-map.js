/* jshint esversion: 11 */
/* global L */

document.addEventListener("DOMContentLoaded", function () {
    const mapElement = document.getElementById("ride-map");
    const dataElement = document.getElementById("ride-map-data");

    if (!mapElement || !dataElement) {
        return;
    }

    const rides = JSON.parse(dataElement.textContent);

    const map = L.map("ride-map").setView(
        [43.238949, 76.889709],
        10
    );

    L.tileLayer(
        "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        {
            maxZoom: 19,
            attribution: "&copy; OpenStreetMap contributors"
        }
    ).addTo(map);

    rides.forEach(function (ride) {
        L.marker([
            ride.start_latitude,
            ride.start_longitude
        ])
            .addTo(map)
            .bindPopup(
                "Start: " + ride.start_name
            );

        L.marker([
            ride.destination_latitude,
            ride.destination_longitude
        ])
            .addTo(map)
            .bindPopup(
                "Destination: "
                + ride.destination_name
            );
    });
});
