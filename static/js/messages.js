/* jshint esversion: 11 */
document.addEventListener("DOMContentLoaded", function () {
    setTimeout(function () {
        const alerts = document.getElementById("alerts");

        if (alerts) {
            alerts.remove();
        }
    }, 3000);
});