/* jshint esversion: 11 */
/* global saveLocationUrl, csrfToken */


if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(function(position) {

        fetch(saveLocationUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken
            },
            body: JSON.stringify({
                latitude: position.coords.latitude,
                longitude: position.coords.longitude
            })
        });

    });
}

const filterBtn =
    document.getElementById("toggle-filter-btn");

const filterBox =
    document.getElementById("filter-box");

if (filterBtn && filterBox) {

    filterBtn.addEventListener(
        "click",
        function(e) {

            e.preventDefault();

            filterBox.style.display =
                filterBox.style.display === "block" ? "none" : "block";
        }
    );
}