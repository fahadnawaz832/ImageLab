
const imageInput = document.getElementById("imageInput");
const browseButton = document.getElementById("browseButton");
const dropZone = document.getElementById("dropZone");
const previewPanel = document.getElementById("previewPanel");
const previewImage = document.getElementById("previewImage");
const fileName = document.getElementById("fileName");
const fileSize = document.getElementById("fileSize");
const fileType = document.getElementById("fileType");
const removeButton = document.getElementById("removeButton");
const uploadForm = document.getElementById("uploadForm");

const MAX_SIZE = 20 * 1024 * 1024;

const allowedExtensions = [
    "jpg", "jpeg", "png", "bmp", "webp"
];

let previewURL = null;


browseButton.addEventListener("click", () => {
    imageInput.click();
});


function formatSize(bytes) {

    if (bytes < 1024) {
        return bytes + " Bytes";
    }

    if (bytes < 1024 * 1024) {
        return (bytes / 1024).toFixed(2) + " KB";
    }

    return (bytes / (1024 * 1024)).toFixed(2) + " MB";
}


function handleFile(file) {

    if (!file) return;

    const extension = file.name.split(".").pop().toLowerCase();

    if (!allowedExtensions.includes(extension)) {
        alert("Invalid format! Please select JPG, PNG, BMP or WEBP.");
        imageInput.value = "";
        return;
    }

    if (file.size > MAX_SIZE) {
        alert("Image size must be less than 20 MB.");
        imageInput.value = "";
        return;
    }

    if (!file.type.startsWith("image/")) {
        alert("Please select a valid image file.");
        imageInput.value = "";
        return;
    }

    if (previewURL) {
        URL.revokeObjectURL(previewURL);
    }

    previewURL = URL.createObjectURL(file);

    previewImage.src = previewURL;

    fileName.textContent = file.name;
    fileSize.textContent = "Size: " + formatSize(file.size);
    fileType.textContent = "Format: " + extension.toUpperCase();

    previewPanel.style.display = "block";

    dropZone.style.display = "none";

    previewPanel.scrollIntoView({
        behavior: "smooth",
        block: "nearest"
    });
}


imageInput.addEventListener("change", (event) => {

    handleFile(event.target.files[0]);

});


dropZone.addEventListener("dragover", (event) => {

    event.preventDefault();

    dropZone.classList.add("drag-over");

});


dropZone.addEventListener("dragleave", () => {

    dropZone.classList.remove("drag-over");

});


dropZone.addEventListener("drop", (event) => {

    event.preventDefault();

    dropZone.classList.remove("drag-over");

    const file = event.dataTransfer.files[0];

    if (!file) return;

    const transfer = new DataTransfer();

    transfer.items.add(file);

    imageInput.files = transfer.files;

    handleFile(file);

});


removeButton.addEventListener("click", () => {

    imageInput.value = "";

    previewImage.src = "";

    previewPanel.style.display = "none";

    dropZone.style.display = "flex";

    if (previewURL) {
        URL.revokeObjectURL(previewURL);
        previewURL = null;
    }

});


uploadForm.addEventListener("submit", (event) => {

    if (!imageInput.files.length) {

        event.preventDefault();

        alert("Please select an image first.");

    } else {

        const submitButton = uploadForm.querySelector(
            ".upload-submit"
        );

        submitButton.textContent = "Uploading...";

        submitButton.disabled = true;

    }

});