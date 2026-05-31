/* jshint esversion: 11 */

const callProtocol =
    window.location.protocol === "https:" ? "wss://" : "ws://";

const globalCallSocket = new WebSocket(
    callProtocol + window.location.host + "/ws/calls/"
);

globalCallSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);

    if (data.type === "incoming_call") {
        const callPanel = document.getElementById("call-panel");
        const statusText = document.getElementById("call-status");

        callPanel.classList.remove("hidden");

        statusText.innerText =
            `${data.username} is calling you...`;

        document.getElementById("accept-call").onclick = function() {
            window.location.href = `/chat/${data.room_id}/`;
        };

        document.getElementById("decline-call").onclick = function() {
            callPanel.classList.add("hidden");
        };
    }
};
