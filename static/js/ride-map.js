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

    function escapeHtml(value) {
        const element = document.createElement("div");
        element.textContent = String(value ?? "");
        return element.innerHTML;
    }

    rides.forEach(function (ride) {
        const departureDate = new Date(
            ride.departure_time
        );

        const formattedDeparture =
            departureDate.toLocaleString();

        const startPopup = `
            <strong>
                Start:
                ${escapeHtml(ride.start_name)}
            </strong>

            <p>
                Destination:
                ${escapeHtml(ride.destination_name)}
            </p>

            <p>
                Departure:
                ${escapeHtml(formattedDeparture)}
            </p>

            <p>
                Remaining seats:
                ${escapeHtml(ride.remaining_seats)}
            </p>

            <a href="${ride.detail_url}">
                View ride
            </a>
        `;

        const destinationPopup = `
            <strong>
                Destination:
                ${escapeHtml(ride.destination_name)}
            </strong>

            <p>
                Starting point:
                ${escapeHtml(ride.start_name)}
            </p>

            <a href="${ride.detail_url}">
                View ride
            </a>
        `;

        L.marker([
            ride.start_latitude,
            ride.start_longitude
        ])
            .addTo(map)
            .bindPopup(startPopup);

        L.marker([
            ride.destination_latitude,
            ride.destination_longitude
        ])
            .addTo(map)
            .bindPopup(destinationPopup);
    });
});
