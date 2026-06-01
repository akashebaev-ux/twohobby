/* jshint esversion: 11 */

const callPanel = document.getElementById("global-call-panel");

if (callPanel) {
    const callProtocol =
        window.location.protocol === "https:" ? "wss://" : "ws://";

    const globalCallSocket = new WebSocket(
        callProtocol + window.location.host + "/ws/calls/"
    );

    window.addEventListener("beforeunload", function() {
        globalCallSocket.close();
    });

    globalCallSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);

        console.log("Incoming global call data:", data);

        if (data.type === "incoming_call") {
            const statusText =
                document.getElementById("global-call-status");

            callPanel.classList.remove("hidden");

            statusText.innerText =
                `${data.username} is calling you...`;

            document.getElementById("global-accept-call").onclick =
            function() {
                sessionStorage.setItem(
                    "acceptIncomingCall",
                    "true"
                );

                window.location.href =
                    `/chat/${data.room_id}/`;
            };

            document.getElementById("global-decline-call").onclick =
            function() {
                callPanel.classList.add("hidden");
            };
        }
    };
}
