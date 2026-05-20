function showCallInvite(username) {
    const callPanel = document.getElementById("call-panel");
    const statusText = document.getElementById("call-status");

    callPanel.classList.remove("hidden");
    statusText.innerText = `${username} is calling you...`;
}

const openCallBtn = document.getElementById("open-call-ui");
const callPanel = document.getElementById("call-panel");
const declineCallBtn = document.getElementById("decline-call");
const acceptBtn = document.getElementById("accept-call");

let peerConnection;
let localStream;
let remoteStream;
let isCalling = false;

const rtcConfig = {
    iceServers: [
        {
            urls: "stun:stun.l.google.com:19302"
        }
    ]
};

openCallBtn.onclick = function() {
    callPanel.classList.remove("hidden");

    window.chatSocket.send(JSON.stringify({
        type: "call_invite"
    }));
};

function endCallAfterOneMinute() {
    setTimeout(() => {
        if (peerConnection) {
            peerConnection.close();
            peerConnection = null;
        }

        if (localStream) {
            localStream.getTracks().forEach(track => {
                track.stop();
            });

            localStream = null;
        }

        document.getElementById("call-status").innerText =
            "1 minute limit reached";

        callPanel.classList.add("hidden");
    }, 60000);
}

async function startWebRTCCall() {
    if (!localStream) {
        localStream = await navigator.mediaDevices.getUserMedia({
            audio: {
                echoCancellation: true,
                noiseSuppression: true,
                autoGainControl: false
            },
            video: false
        });
    }

    remoteStream = new MediaStream();

    document.getElementById("remote-audio").srcObject = remoteStream;

    peerConnection = new RTCPeerConnection(rtcConfig);

    localStream.getTracks().forEach(function(track) {
        peerConnection.addTrack(track, localStream);
    });

    peerConnection.ontrack = function(event) {
        const remoteAudio = document.getElementById("remote-audio");

        remoteAudio.srcObject = event.streams[0];
        remoteAudio.volume = 0.05;
        remoteAudio.setAttribute("controls", false);
    };

    peerConnection.onicecandidate = function(event) {
        if (event.candidate) {
            window.chatSocket.send(JSON.stringify({
                type: "ice_candidate",
                candidate: event.candidate
            }));
        }
    };
}

async function handleWebRTCOffer(offer) {
    await startWebRTCCall();

    await peerConnection.setRemoteDescription(
        new RTCSessionDescription(offer)
    );

    const answer = await peerConnection.createAnswer();

    await peerConnection.setLocalDescription(answer);

    window.chatSocket.send(JSON.stringify({
        type: "webrtc_answer",
        answer: answer
    }));

    document.getElementById("call-status").innerText = "Call connected";
}

async function handleWebRTCAnswer(answer) {
    await peerConnection.setRemoteDescription(
        new RTCSessionDescription(answer)
    );

    document.getElementById("call-status").innerText = "Call connected";
}

async function handleIceCandidate(candidate) {
    if (peerConnection) {
        await peerConnection.addIceCandidate(
            new RTCIceCandidate(candidate)
        );
    }
}

acceptBtn.onclick = async function() {
    isCalling = true;

    await startWebRTCCall();

    endCallAfterOneMinute();

    const offer = await peerConnection.createOffer();

    await peerConnection.setLocalDescription(offer);

    window.chatSocket.send(JSON.stringify({
        type: "webrtc_offer",
        offer: offer
    }));

    document.getElementById("call-status").innerText = "Calling...";
};

declineCallBtn.onclick = function() {
    isCalling = false;

    document.getElementById("call-status").innerText = "Call ended";

    if (peerConnection) {
        peerConnection.close();
        peerConnection = null;
    }

    if (localStream) {
        localStream.getTracks().forEach(track => {
            track.stop();
        });

        localStream = null;
    }

    callPanel.classList.add("hidden");
};