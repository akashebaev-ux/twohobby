window.speakText =
function(text, lang = "en") {

    const voiceMap = {
        en: "en-US",
        sv: "sv-SE",
        fr: "fr-FR",
        ru: "ru-RU",
        kk: "kk-KZ"
    };

    const utterance =
        new SpeechSynthesisUtterance(
            text
        );

    utterance.lang =
        voiceMap[lang] || "en-US";

    speechSynthesis.speak(
        utterance
    );
};