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

        const tileUrl = (
            mapElement.dataset.tileUrl
        );

        const tileAttribution = (
            mapElement.dataset.tileAttribution
            || "&copy; OpenStreetMap contributors"
        );

        if (!tileUrl) {
            console.error(
                "The map tile URL is missing."
            );
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

        const pickupIcon = L.divIcon({
            className: "ride-map-marker-wrapper",
            html: `
                <span
                    class="
                        ride-map-marker
                        ride-map-marker--pickup
                    "
                    aria-hidden="true"
                ></span>
            `,
            iconSize: [24, 24],
            iconAnchor: [12, 12],
            popupAnchor: [0, -14],
        });

        const destinationIcon = L.divIcon({
            className: "ride-map-marker-wrapper",
            html: `
                <span
                    class="
                        ride-map-marker
                        ride-map-marker--destination
                    "
                    aria-hidden="true"
                ></span>
            `,
            iconSize: [24, 24],
            iconAnchor: [12, 12],
            popupAnchor: [0, -14],
        });

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
                ride.destination_longitude,
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
                Number(ride.start_longitude),
            ];

            const destinationCoordinates = [
                Number(ride.destination_latitude),
                Number(ride.destination_longitude),
            ];

            const departureDate = new Date(
                ride.departure_time
            );

            const formattedDeparture = (
                Number.isNaN(
                    departureDate.getTime()
                )
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
                startCoordinates,
                {
                    icon: pickupIcon,
                }
            )
                .addTo(map)
                .bindPopup(startPopup);

            const destinationMarker = L.marker(
                destinationCoordinates,
                {
                    icon: destinationIcon,
                }
            )
                .addTo(map)
                .bindPopup(destinationPopup);

            allRouteBounds.push(
                startMarker.getLatLng()
            );

            allRouteBounds.push(
                destinationMarker.getLatLng()
            );

            const fallbackLine = L.polyline(
                [
                    startCoordinates,
                    destinationCoordinates,
                ],
                {
                    color: "#171717",
                    weight: 5,
                    opacity: 0.45,
                    dashArray: "10, 8",
                    lineCap: "round",
                    lineJoin: "round",
                }
            ).addTo(map);

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

            try {
                const response = await fetch(
                    routeUrl
                );

                if (!response.ok) {
                    throw new Error(
                        "Routing request failed: "
                        + response.status
                    );
                }

                const routeData = (
                    await response.json()
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

                if (
                    !route.geometry
                    || !Array.isArray(
                        route.geometry.coordinates
                    )
                ) {
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

                map.removeLayer(
                    fallbackLine
                );

                const routeCoordinates = (
                    route.geometry.coordinates.map(
                        function (coordinate) {
                            return [
                                coordinate[1],
                                coordinate[0],
                            ];
                        }
                    )
                );

                const routeShadow = L.polyline(
                    routeCoordinates,
                    {
                        color: "#000000",
                        weight: 10,
                        opacity: 0.18,
                        lineCap: "round",
                        lineJoin: "round",
                        interactive: false,
                    }
                ).addTo(map);

                const routeLine = L.polyline(
                    routeCoordinates,
                    {
                        color: "#171717",
                        weight: 6,
                        opacity: 1,
                        lineCap: "round",
                        lineJoin: "round",
                    }
                ).addTo(map);

                routeLine.bindPopup(
                    routePopup
                );

                routeShadow.bringToBack();
                routeLine.bringToFront();

                startMarker.bringToFront();
                destinationMarker.bringToFront();

                allRouteBounds.push(
                    routeLine.getBounds()
                );
            } catch (error) {
                console.error(
                    "Could not load road route:",
                    error
                );

                fallbackLine.bindPopup(
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

                fallbackLine.bringToFront();

                startMarker.bringToFront();
                destinationMarker.bringToFront();

                allRouteBounds.push(
                    fallbackLine.getBounds()
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
                        maxZoom: 15,
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
