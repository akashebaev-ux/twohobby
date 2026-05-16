import { pipeline }
from "https://cdn.jsdelivr.net/npm/@huggingface/transformers";

let transcriber = null;

async function loadWhisper() {

    if (!transcriber) {

        transcriber = await pipeline(
            "automatic-speech-recognition",
            "Xenova/whisper-tiny"
        );
    }

    return transcriber;
}

window.transcribeAudio =
async function(audioBlob) {

    const whisper =
        await loadWhisper();

    const result =
        await whisper(audioBlob);

    return result.text;
}