window.translateText =
async function(text, targetLanguage = "en") {

    const response = await fetch(
        "https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl="
        + targetLanguage +
        "&dt=t&q=" +
        encodeURIComponent(text)
    );

    const data = await response.json();

    return data[0][0][0];
};