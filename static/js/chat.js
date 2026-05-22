/* jshint esversion: 11 */
/* global roomId, currentUser, showCallInvite,
handleWebRTCOffer, handleWebRTCAnswer, handleIceCandidate */


const protocol =
    window.location.protocol === "https:" ? "wss://" : "ws://";

window.chatSocket = new WebSocket(
    protocol + window.location.host + "/ws/chat/" + roomId + "/"
);

window.chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);

    if (data.type === "call_limit") {
        alert(data.message);
        return;
    }

    if (data.type === "image") {
        const messageClass =
            data.username === currentUser ? "my-message" : "their-message";

        const chatLog = document.querySelector("#chat-log");

        chatLog.insertAdjacentHTML("beforeend", `
            <div class="chat-message ${messageClass}">
                <img
                    src="${data.image_url.replace(
                        "/upload/",
                        "/upload/f_auto,q_auto,w_300,h_300,c_fill,g_auto/"
                    )}"
                    loading="lazy"
                    class="chat-image"
                    alt="Chat image"
                >
                <span>${new Date().toLocaleTimeString([], {
                    hour: "2-digit",
                    minute: "2-digit"
                })}</span>
            </div>
        `);

        const newImage =
            chatLog.querySelector(".chat-message:last-child img");

        if (newImage) {
            newImage.addEventListener("load", scrollToBottom);
        }

        scrollToBottom();
        return;
    }

    if (
        data.username === currentUser &&
        [
            "webrtc_offer",
            "webrtc_answer",
            "ice_candidate",
            "call_invite"
        ].includes(data.type)
    ) {
        return;
    }

    if (data.type === "call_invite") {
        showCallInvite(data.username);
        return;
    }

    if (data.type === "webrtc_offer") {
        handleWebRTCOffer(data.offer);
        return;
    }

    if (data.type === "webrtc_answer") {
        handleWebRTCAnswer(data.answer);
        return;
    }

    if (data.type === "ice_candidate") {
        handleIceCandidate(data.candidate);
        return;
    }

    const messageClass =
        data.username === currentUser ? "my-message" : "their-message";

    const chatLog = document.querySelector("#chat-log");

    chatLog.insertAdjacentHTML("beforeend", `
        <div class="chat-message ${messageClass}">
            <p>${data.message}</p>
            <span>${new Date().toLocaleTimeString([], {
                hour: "2-digit",
                minute: "2-digit"
            })}</span>
        </div>
    `);

    scrollToBottom();
};

document.querySelector("#chat-message-submit").onclick = function() {
    const messageInput = document.querySelector("#chat-message-input");
    const message = messageInput.value.trim();
    const imageInput = document.querySelector("#chat-image-input");
    const image = imageInput.files[0];

    if (image && image.size > 2 * 1024 * 1024) {
        alert("Image must be smaller than 2MB.");
        return;
    }

    if (message === "" && !image) {
        return;
    }

    if (window.chatSocket.readyState !== WebSocket.OPEN) {
        window.location.reload();
        return;
    }

    window.chatSocket.send(JSON.stringify({
        message: message,
        is_voice: false
    }));

    messageInput.value = "";
    messageInput.focus();
    scrollToBottom();
};

document.querySelector("#chat-message-input").addEventListener(
    "keyup",
    function(e) {
        if (e.key === "Enter") {
            document.querySelector("#chat-message-submit").click();
        }
    }
);

function scrollToBottom() {
    const chatLog = document.querySelector("#chat-log");

    if (!chatLog) {
        return;
    }

    function doScroll() {
        chatLog.scrollTop = chatLog.scrollHeight;
    }

    requestAnimationFrame(doScroll);
    setTimeout(doScroll, 100);
    setTimeout(doScroll, 300);
    setTimeout(doScroll, 1000);
}

window.addEventListener("DOMContentLoaded", function() {
    scrollToBottom();
});

window.addEventListener("pageshow", function() {
    const messageInput = document.querySelector("#chat-message-input");

    if (messageInput) {
        messageInput.disabled = false;
    }
    scrollToBottom();
});
