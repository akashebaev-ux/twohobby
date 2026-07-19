/* jshint esversion: 11 */
/* global L */

document.addEventListener(
    "DOMContentLoaded",
    async function () {
        const mapElement = document.getElementById(
            "ride-map"
        );

        const dataElement = document.getElementById(
            "ride-map-data"
        );

        if (!mapElement || !dataElement) {
            console.error(
                "Ride map container or map data is missing."
            );
            return;
        }

        let rides = [];

        try {
            rides = JSON.parse(
                dataElement.textContent
            );
        } catch (error) {
            console.error(
                "Could not parse ride map data:",
                error
            );
            return;
        }


        const almatyBounds = L.latLngBounds(
            [43.05, 76.65],
            [43.40, 77.20]
        );

        const map = L.map(
            "ride-map",
            {
                minZoom: 10,
                maxZoom: 18,
                maxBounds: almatyBounds,
                maxBoundsViscosity: 1.0,
                zoomControl: false,
            }
        ).setView(
            [43.238949, 76.889709],
            12
        );

        L.control.zoom({
            position: "topright",
        }).addTo(map);

        const tileUrl = mapElement.dataset.tileUrl;
        const tileAttribution = (
            mapElement.dataset.tileAttribution
            || "&copy; OpenStreetMap contributors"
        );

        if (!tileUrl) {
            console.error("The map tile URL is missing.");
            return;
        }

        L.tileLayer(
            tileUrl,
            {
                minZoom: 10,
                maxZoom: 18,
                attribution: tileAttribution,
            }
        ).addTo(map);

        function escapeHtml(value) {
            const element = document.createElement(
                "div"
            );

            element.textContent = String(
                value ?? ""
            );

            return element.innerHTML;
        }

        function isValidCoordinate(value) {
            return (
                value !== null
                && value !== undefined
                && value !== ""
                && Number.isFinite(Number(value))
            );
        }

        function createMarkerPopup(
            title,
            ride,
            formattedDeparture
        ) {
            return `
                <strong>
                    ${escapeHtml(title)}
                </strong>

                <p>
                    Start:
                    ${escapeHtml(
                        ride.start_name
                    )}
                </p>

                <p>
                    Destination:
                    ${escapeHtml(
                        ride.destination_name
                    )}
                </p>

                <p>
                    Departure:
                    ${escapeHtml(
                        formattedDeparture
                    )}
                </p>

                <p>
                    Remaining seats:
                    ${escapeHtml(
                        ride.remaining_seats
                    )}
                </p>

                <a href="${escapeHtml(
                    ride.detail_url
                )}">
                    View ride
                </a>
            `;
        }

        const allRouteBounds = [];

        async function drawRideRoute(ride) {
            const requiredCoordinates = [
                ride.start_latitude,
                ride.start_longitude,
                ride.destination_latitude,
                ride.destination_longitude
            ];

            const hasValidCoordinates = (
                requiredCoordinates.every(
                    isValidCoordinate
                )
            );

            if (!hasValidCoordinates) {
                console.error(
                    "Ride has invalid coordinates:",
                    ride
                );
                return;
            }

            const startCoordinates = [
                Number(ride.start_latitude),
                Number(ride.start_longitude)
            ];

            const destinationCoordinates = [
                Number(ride.destination_latitude),
                Number(ride.destination_longitude)
            ];

            console.log(
                "Coordinates:",
                startCoordinates,
                destinationCoordinates
            );

            const departureDate = new Date(
                ride.departure_time
            );

            const formattedDeparture = (
                Number.isNaN(departureDate.getTime())
                    ? String(ride.departure_time)
                    : departureDate.toLocaleString()
            );

            const startPopup = createMarkerPopup(
                "Starting point",
                ride,
                formattedDeparture
            );

            const destinationPopup = (
                createMarkerPopup(
                    "Destination",
                    ride,
                    formattedDeparture
                )
            );

            const startMarker = L.marker(
                startCoordinates
            )
                .addTo(map)
                .bindPopup(startPopup);

            const destinationMarker = L.marker(
                destinationCoordinates
            )
                .addTo(map)
                .bindPopup(destinationPopup);

            allRouteBounds.push(
                startMarker.getLatLng()
            );

            allRouteBounds.push(
                destinationMarker.getLatLng()
            );

            const testLine = L.polyline(
                [
                    startCoordinates,
                    destinationCoordinates
                ],
                {
                    color: "#ff0000",
                    weight: 4,
                    opacity: 0.45,
                    dashArray: "8, 8"
                }
            ).addTo(map);

            testLine.bringToFront();

            const routeUrl = (
                "https://router.project-osrm.org/"
                + "route/v1/driving/"
                + ride.start_longitude
                + ","
                + ride.start_latitude
                + ";"
                + ride.destination_longitude
                + ","
                + ride.destination_latitude
                + "?overview=full"
                + "&geometries=geojson"
                + "&steps=false"
            );

            console.log(
                "OSRM URL:",
                routeUrl
            );

            try {
                const response = await fetch(
                    routeUrl
                );

                if (!response.ok) {
                    throw new Error(
                        `Routing request failed: `
                        + `${response.status}`
                    );
                }

                const routeData = (
                    await response.json()
                );

                console.log(
                    "OSRM result:",
                    routeData
                );

                if (
                    routeData.code !== "Ok"
                    || !Array.isArray(
                        routeData.routes
                    )
                    || routeData.routes.length === 0
                ) {
                    throw new Error(
                        "No road route was found."
                    );
                }

                const route = (
                    routeData.routes[0]
                );

                if (!route.geometry) {
                    throw new Error(
                        "Route geometry is missing."
                    );
                }

                const distanceKilometres = (
                    route.distance / 1000
                ).toFixed(1);

                const durationMinutes = Math.round(
                    route.duration / 60
                );

                const routePopup = `
                    <strong>
                        ${escapeHtml(
                            ride.start_name
                        )}
                        →
                        ${escapeHtml(
                            ride.destination_name
                        )}
                    </strong>

                    <p>
                        Distance:
                        ${escapeHtml(
                            distanceKilometres
                        )}
                        km
                    </p>

                    <p>
                        Estimated time:
                        ${escapeHtml(
                            durationMinutes
                        )}
                        minutes
                    </p>

                    <p>
                        Remaining seats:
                        ${escapeHtml(
                            ride.remaining_seats
                        )}
                    </p>

                    <a href="${escapeHtml(
                        ride.detail_url
                    )}">
                        View ride
                    </a>
                `;

                map.removeLayer(testLine);

                const routeLayer = L.geoJSON(
                    route.geometry,
                    {
                        style: {
                            color: "#ff0000",
                            weight: 8,
                            opacity: 1
                        }
                    }
                ).addTo(map);

                routeLayer.bindPopup(
                    routePopup
                );

                routeLayer.bringToFront();

                console.log(
                    "Route layer added:",
                    routeLayer.getBounds()
                );

                allRouteBounds.push(
                    routeLayer.getBounds()
                );
            } catch (error) {
                console.error(
                    "Could not load road route:",
                    error
                );

                testLine.setStyle(
                    {
                        color: "#A30088",
                        weight: 6,
                        opacity: 0.85,
                        dashArray: "10, 8"
                    }
                );

                testLine.bindPopup(
                    `
                        <strong>
                            Route unavailable
                        </strong>

                        <p>
                            A direct line is shown because
                            the road routing service could
                            not return a route.
                        </p>

                        <a href="${escapeHtml(
                            ride.detail_url
                        )}">
                            View ride
                        </a>
                    `
                );

                allRouteBounds.push(
                    testLine.getBounds()
                );
            }
        }

        for (const ride of rides) {
            await drawRideRoute(ride);
        }

        if (allRouteBounds.length > 0) {
            const combinedBounds = (
                L.latLngBounds([])
            );

            allRouteBounds.forEach(
                function (bounds) {
                    combinedBounds.extend(
                        bounds
                    );
                }
            );

            if (combinedBounds.isValid()) {
                map.fitBounds(
                    combinedBounds,
                    {
                        padding: [30, 30],
                        maxZoom: 15
                    }
                );
            }
        } else {
            console.warn(
                "No rides with valid coordinates were found."
            );
        }

        window.setTimeout(
            function () {
                map.invalidateSize();
            },
            200
        );
    }
);
