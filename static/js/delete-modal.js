/* jshint esversion: 11 */

function openDeleteModal(button) {
    const form = button.closest('form');
    const modal = form.querySelector('.delete-modal');
    modal.style.display = 'flex';
}

function closeDeleteModal(button) {
    const modal = button.closest('.delete-modal');
    modal.style.display = 'none';
}

window.openDeleteModal = openDeleteModal;
window.closeDeleteModal = closeDeleteModal;
