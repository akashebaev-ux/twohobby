/* jshint esversion: 11 */

const carousel = document.getElementById("liked-carousel");
let scrollSpeed = 0;

function animate() {
    if (carousel && scrollSpeed !== 0) {
        carousel.scrollLeft += scrollSpeed;
    }

    requestAnimationFrame(animate);
}

if (carousel) {
    carousel.addEventListener("mousemove", (e) => {
        const rect = carousel.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const width = rect.width;
        const edgeZone = 80;

        if (mouseX < edgeZone) {
            scrollSpeed = -8;
        } else if (mouseX > width - edgeZone) {
            scrollSpeed = 8;
        } else {
            scrollSpeed = 0;
        }
    });

    carousel.addEventListener("mouseleave", () => {
        scrollSpeed = 0;
    });
}

animate();
