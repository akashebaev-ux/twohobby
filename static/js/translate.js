window.translateText =
async function(text) {

    const response = await fetch(
        "https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=en&dt=t&q="
        + encodeURIComponent(text)
    );

    const data = await response.json();

    return data[0][0][0];
};