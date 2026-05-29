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

const minAgeInput =
    document.querySelector("input[name='min_age']");

const maxAgeInput =
    document.querySelector("input[name='max_age']");

function validateAgeInput(input) {

    input.addEventListener("input", function() {

        this.value =
            this.value.replace(/[^0-9]/g, "");

        const age =
            Number(this.value);

        if (this.value && (age < 18 || age > 100)) {

            this.setCustomValidity(
                "Age must be between 18 and 100."
            );

        } else {

            this.setCustomValidity("");
        }
    });
}

if (minAgeInput) {
    validateAgeInput(minAgeInput);
}

if (maxAgeInput) {
    validateAgeInput(maxAgeInput);
}