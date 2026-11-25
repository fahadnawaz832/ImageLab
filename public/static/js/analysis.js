
const sourceImage = document.getElementById("sourceImage");
const canvas = document.getElementById("pixelCanvas");

const ctx = canvas.getContext("2d", {
    willReadFrequently: true
});

const colorPreview = document.getElementById("colorPreview");

sourceImage.addEventListener("load", () => {

    canvas.width = sourceImage.naturalWidth;
    canvas.height = sourceImage.naturalHeight;

    ctx.drawImage(
        sourceImage,
        0,
        0,
        canvas.width,
        canvas.height
    );

});
if (sourceImage.complete && sourceImage.naturalWidth) {
    sourceImage.dispatchEvent(new Event("load"));
}

canvas.addEventListener("mousemove", (event) => {

    const rect = canvas.getBoundingClientRect();

    const x = Math.floor(
        (event.clientX - rect.left) * canvas.width / rect.width
    );

    const y = Math.floor(
        (event.clientY - rect.top) * canvas.height / rect.height
    );

    if (
        x < 0 || y < 0 ||
        x >= canvas.width || y >= canvas.height
    ) {
        return;
    }

    const pixel = ctx.getImageData(x, y, 1, 1).data;

    const red = pixel[0];
    const green = pixel[1];
    const blue = pixel[2];

    const hex = "#" + [red, green, blue]
        .map(value => value.toString(16).padStart(2, "0"))
        .join("")
        .toUpperCase();

    document.getElementById("pixelX").textContent = x;
    document.getElementById("pixelY").textContent = y;

    document.getElementById("redValue").textContent = red;
    document.getElementById("greenValue").textContent = green;
    document.getElementById("blueValue").textContent = blue;

    document.getElementById("hexValue").textContent = hex;

    colorPreview.style.backgroundColor = hex;

});


canvas.addEventListener("mouseleave", () => {

    document.getElementById("pixelX").textContent = "--";
    document.getElementById("pixelY").textContent = "--";

    document.getElementById("redValue").textContent = "--";
    document.getElementById("greenValue").textContent = "--";
    document.getElementById("blueValue").textContent = "--";

    document.getElementById("hexValue").textContent = "--";

    colorPreview.style.backgroundColor = "#252d45";

});
