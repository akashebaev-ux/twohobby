window.speakText =
function(text, lang = "en-US") {

    const utterance =
        new SpeechSynthesisUtterance(
            text
        );

    utterance.lang = lang;

    speechSynthesis.speak(
        utterance
    );
};