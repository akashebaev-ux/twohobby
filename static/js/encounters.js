/* jshint esversion: 11 */


const filterBtn =
    document.getElementById("toggle-filter-btn");

const filterBox =
    document.getElementById("filter-box");

if (filterBtn && filterBox) {

    filterBtn.addEventListener(

        "click",

        function(e) {

            e.preventDefault();

            if (filterBox.style.display === "block") {

                filterBox.style.display = "none";

            } else {

                filterBox.style.display = "block";
            }
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