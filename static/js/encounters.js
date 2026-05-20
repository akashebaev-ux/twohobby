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