
import os
import uuid

from flask import (
    Flask, render_template, request,
    redirect, url_for, abort, send_from_directory
)
from werkzeug.utils import secure_filename
from PIL import Image, UnidentifiedImageError

from image_processing.analysis import analyze_image
from image_processing.histogram import generate_histogram, equalize_image
from image_processing.filters import apply_filter
from image_processing.enhancement import enhance_image
from image_processing.compression import compress_image as create_compressed_image


app = Flask(__name__)

app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024

app.config["UPLOAD_FOLDER"] = os.path.join(
    app.root_path, "static", "uploads"
)

app.config["RESULT_FOLDER"] = os.path.join(
    app.root_path, "static", "results"
)

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(app.config["RESULT_FOLDER"], exist_ok=True)


ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "bmp", "webp"}

ALLOWED_FILTERS = {
    "grayscale", "gaussian", "median", "edge",
    "sharpen", "brightness", "contrast"
}

ALLOWED_RESULT_TYPES = {"equalized", "filtered", "enhanced"}


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def valid_filename(filename):
    return (
        bool(filename)
        and "/" not in filename
        and "\\" not in filename
        and allowed_file(filename)
    )


def get_original_stem(filename):
    """Remove the UUID from the stored upload filename."""

    stem = os.path.splitext(filename)[0]
    parts = stem.rsplit("_", 1)

    if len(parts) == 2 and len(parts[1]) == 32:
        try:
            uuid.UUID(hex=parts[1])
            return parts[0]
        except ValueError:
            pass

    return stem


def get_upload_path(filename):
    if not valid_filename(filename):
        abort(404)

    path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    if not os.path.isfile(path):
        abort(404)

    return path


def create_result_filename(original_filename, suffix):
    original_stem = get_original_stem(original_filename)
    unique_id = uuid.uuid4().hex

    result_filename = (
        f"{original_stem}_{suffix}_{unique_id}.png"
    )

    download_name = f"{original_stem}_{suffix}.png"

    return result_filename, download_name


def validate_result(filename, result, suffix):
    if suffix not in ALLOWED_RESULT_TYPES:
        abort(404)

    if (
        not result
        or "/" in result
        or "\\" in result
        or not result.endswith(".png")
    ):
        abort(404)

    original_stem = get_original_stem(filename)
    expected_prefix = f"{original_stem}_{suffix}_"

    if not result.startswith(expected_prefix):
        abort(404)

    result_path = os.path.join(
        app.config["RESULT_FOLDER"], result
    )

    if not os.path.isfile(result_path):
        abort(404)

    return f"{original_stem}_{suffix}.png"


def format_file_size(size):
    """Convert bytes into readable KB or MB."""

    if size >= 1024 * 1024:
        return f"{size / (1024 * 1024):.2f} MB"

    return f"{size / 1024:.2f} KB"


# --------------------------------------------------
# HOMEPAGE / IMAGE UPLOAD
# --------------------------------------------------

@app.route("/", methods=["GET", "POST"])
def home():
    uploaded_image = None
    uploaded_name = None
    error = None
    success = None

    if request.method == "POST":
        file = request.files.get("image")

        if not file or file.filename == "":
            error = "Please select an image."

        elif not allowed_file(file.filename):
            error = "Unsupported image format."

        else:
            original_name = secure_filename(file.filename)

            if not original_name or not allowed_file(original_name):
                error = "Invalid filename."

            else:
                original_stem = os.path.splitext(original_name)[0]
                extension = original_name.rsplit(".", 1)[1].lower()

                unique_name = (
                    f"{original_stem}_{uuid.uuid4().hex}.{extension}"
                )

                save_path = os.path.join(
                    app.config["UPLOAD_FOLDER"], unique_name
                )

                try:
                    image = Image.open(file)
                    image.verify()

                    file.seek(0)
                    file.save(save_path)

                    uploaded_image = f"uploads/{unique_name}"
                    uploaded_name = original_name
                    success = "Image uploaded successfully!"

                except (UnidentifiedImageError, OSError, ValueError):
                    error = "Invalid or corrupted image file."

    return render_template(
        "index.html",
        uploaded_image=uploaded_image,
        uploaded_name=uploaded_name,
        error=error,
        success=success
    )


# --------------------------------------------------
# IMAGE ANALYSIS
# --------------------------------------------------

@app.route("/analysis/<filename>")
def image_analysis(filename):
    image_path = get_upload_path(filename)

    try:
        analysis = analyze_image(image_path)
    except (ValueError, OSError):
        abort(400)

    return render_template(
        "analysis.html",
        filename=filename,
        analysis=analysis
    )


# --------------------------------------------------
# HISTOGRAM PAGE
# --------------------------------------------------

@app.route("/histogram/<filename>")
def histogram_page(filename):
    image_path = get_upload_path(filename)

    try:
        histogram_data = generate_histogram(image_path)
        is_grayscale = histogram_data["is_grayscale"]
    except (ValueError, OSError, KeyError):
        abort(400)

    result = request.args.get("result")
    download_name = None
    download_url = None

    if result:
        download_name = validate_result(
            filename, result, "equalized"
        )

        download_url = url_for(
            "download_result",
            filename=filename,
            suffix="equalized",
            result=result
        )

    return render_template(
        "histogram.html",
        filename=filename,
        histogram_data=histogram_data,
        is_grayscale=is_grayscale,
        result=result,
        download_name=download_name,
        download_url=download_url
    )


# --------------------------------------------------
# HISTOGRAM EQUALIZATION
# --------------------------------------------------

@app.route("/equalize/<filename>", methods=["POST"])
def equalize_route(filename):
    image_path = get_upload_path(filename)

    output_filename, _ = create_result_filename(
        filename, "equalized"
    )

    output_path = os.path.join(
        app.config["RESULT_FOLDER"], output_filename
    )

    try:
        equalize_image(image_path, output_path)

        if not os.path.isfile(output_path):
            raise ValueError("Equalized image was not created.")

    except (ValueError, OSError):
        abort(400)

    return redirect(url_for(
        "histogram_page",
        filename=filename,
        result=output_filename
    ))


# --------------------------------------------------
# FILTERS PAGE
# --------------------------------------------------

@app.route("/filters/<filename>")
def filters_page(filename):
    get_upload_path(filename)

    result = request.args.get("result")
    download_name = None
    download_url = None

    if result:
        download_name = validate_result(
            filename, result, "filtered"
        )

        download_url = url_for(
            "download_result",
            filename=filename,
            suffix="filtered",
            result=result
        )

    return render_template(
        "filters.html",
        filename=filename,
        result=result,
        selected_filter=request.args.get("filter"),
        download_name=download_name,
        download_url=download_url
    )


# --------------------------------------------------
# APPLY IMAGE FILTER
# --------------------------------------------------

@app.route("/filter/<filename>", methods=["POST"])
def apply_image_filter(filename):
    image_path = get_upload_path(filename)

    filter_type = request.form.get("filter_type", "")

    if filter_type not in ALLOWED_FILTERS:
        abort(400)

    try:
        intensity = float(request.form.get("intensity", 1))

        if not -100 <= intensity <= 100:
            abort(400)

        output_filename, _ = create_result_filename(
            filename, "filtered"
        )

        output_path = os.path.join(
            app.config["RESULT_FOLDER"], output_filename
        )

        apply_filter(
            image_path,
            output_path,
            filter_type,
            intensity
        )

        if not os.path.isfile(output_path):
            raise ValueError("Filtered image was not created.")

    except (ValueError, TypeError, OSError):
        abort(400)

    return redirect(url_for(
        "filters_page",
        filename=filename,
        result=output_filename,
        filter=filter_type
    ))


# --------------------------------------------------
# ENHANCEMENT PAGE
# --------------------------------------------------

@app.route("/enhancement/<filename>")
def enhancement_page(filename):
    get_upload_path(filename)

    result = request.args.get("result")
    download_name = None
    download_url = None

    if result:
        download_name = validate_result(
            filename, result, "enhanced"
        )

        download_url = url_for(
            "download_result",
            filename=filename,
            suffix="enhanced",
            result=result
        )

    return render_template(
        "enhancement.html",
        filename=filename,
        result=result,
        download_name=download_name,
        download_url=download_url
    )


# --------------------------------------------------
# APPLY IMAGE ENHANCEMENT
# --------------------------------------------------

@app.route("/enhance/<filename>", methods=["POST"])
def enhance_image_route(filename):
    image_path = get_upload_path(filename)

    try:
        brightness = int(request.form.get("brightness", 0))
        contrast = float(request.form.get("contrast", 1.0))
        rotation = int(request.form.get("rotation", 0))

        width_value = request.form.get("width", "").strip()
        height_value = request.form.get("height", "").strip()

        if not -100 <= brightness <= 100:
            abort(400)

        if not 0.1 <= contrast <= 3.0:
            abort(400)

        if rotation not in (0, 90, 180, 270):
            abort(400)

        if bool(width_value) != bool(height_value):
            abort(400)

        width = int(width_value) if width_value else None
        height = int(height_value) if height_value else None

        if width is not None and not 1 <= width <= 5000:
            abort(400)

        if height is not None and not 1 <= height <= 5000:
            abort(400)

        output_filename, _ = create_result_filename(
            filename, "enhanced"
        )

        output_path = os.path.join(
            app.config["RESULT_FOLDER"], output_filename
        )

        enhance_image(
            image_path,
            output_path,
            brightness,
            contrast,
            rotation,
            width,
            height
        )

        if not os.path.isfile(output_path):
            raise ValueError("Enhanced image was not created.")

    except (ValueError, TypeError, OSError):
        abort(400)

    return redirect(url_for(
        "enhancement_page",
        filename=filename,
        result=output_filename
    ))


# --------------------------------------------------
# IMAGE COMPRESSION PAGE
# --------------------------------------------------

@app.route("/compression/<filename>")
def compression_page(filename):
    get_upload_path(filename)

    return render_template(
        "compression.html",
        filename=filename,
        compressed=None
    )


# --------------------------------------------------
# COMPRESS IMAGE
# --------------------------------------------------

@app.route("/compress/<filename>", methods=["POST"])
def compress_image(filename):
    image_path = get_upload_path(filename)

    try:
        quality = int(request.form.get("quality", 75))
        output_format = request.form.get("format", "JPEG").upper()

        if not 10 <= quality <= 95:
            abort(400)

        if output_format not in ("JPEG", "WEBP"):
            abort(400)

        result = create_compressed_image(
            image_path,
            app.config["RESULT_FOLDER"],
            quality,
            output_format
        )

        compressed_filename = result["filename"]

        return render_template(
            "compression.html",
            filename=filename,
            compressed=compressed_filename,
            original_size=format_file_size(result["original_size"]),
            compressed_size=format_file_size(result["compressed_size"]),
            savings=result["savings"]
        )

    except (ValueError, TypeError, OSError):
        abort(400)


# --------------------------------------------------
# DOWNLOAD COMPRESSED IMAGE
# --------------------------------------------------

@app.route("/download/compressed/<filename>/<result>")
def download_compressed(filename, result):
    get_upload_path(filename)

    if (
        not result
        or "/" in result
        or "\\" in result
        or not result.startswith("compressed_")
    ):
        abort(404)

    extension = os.path.splitext(result)[1].lower()

    if extension not in (".jpg", ".jpeg", ".webp"):
        abort(404)

    result_path = os.path.join(
        app.config["RESULT_FOLDER"], result
    )

    if not os.path.isfile(result_path):
        abort(404)

    original_stem = get_original_stem(filename)
    clean_name = f"{original_stem}_compressed{extension}"

    return send_from_directory(
        app.config["RESULT_FOLDER"],
        result,
        as_attachment=True,
        download_name=clean_name,
        max_age=0
    )


# --------------------------------------------------
# FORCE DOWNLOAD WITH CLEAN FILENAME
# --------------------------------------------------

@app.route("/download/<filename>/<suffix>/<result>")
def download_result(filename, suffix, result):
    get_upload_path(filename)

    clean_name = validate_result(
        filename, result, suffix
    )

    return send_from_directory(
        app.config["RESULT_FOLDER"],
        result,
        as_attachment=True,
        download_name=clean_name,
        max_age=0
    )


# --------------------------------------------------
# BACKGROUND REMOVAL PAGE
# --------------------------------------------------

# --------------------------------------------------
# BACKGROUND REMOVAL PAGE
# --------------------------------------------------

@app.route("/background-removal/<filename>", methods=["GET", "POST"])
def background_removal_page(filename):

    image_path = get_upload_path(filename)

    result = None
    error = None

    if request.method == "POST":

        try:
            from image_processing.background_removal import remove_background

            result = remove_background(
                image_path,
                app.config["RESULT_FOLDER"]
            )

            if not result or not result.startswith("background_removed_"):
                raise ValueError("Background removal failed.")

        except Exception:
            error = "Background removal is currently unavailable on this deployment."

    return render_template(
        "background_removal.html",
        filename=filename,
        result=result,
        error=error
    )



# --------------------------------------------------
# DOWNLOAD BACKGROUND REMOVED IMAGE
# --------------------------------------------------

@app.route("/download/background-removed/<filename>/<result>")
def download_background_removed(filename, result):

    get_upload_path(filename)

    if (
        not result
        or "/" in result
        or "\\" in result
        or not result.startswith("background_removed_")
        or not result.endswith(".png")
    ):
        abort(404)

    result_path = os.path.join(
        app.config["RESULT_FOLDER"],
        result
    )

    if not os.path.isfile(result_path):
        abort(404)

    original_stem = get_original_stem(filename)
    clean_name = f"{original_stem}_removed.png"

    return send_from_directory(
        app.config["RESULT_FOLDER"],
        result,
        as_attachment=True,
        download_name=clean_name,
        max_age=0
    )

# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@app.route("/health")
def health():
    return {
        "status": "success",
        "message": "ImageLab backend is running!"
    }


# --------------------------------------------------
# ERROR HANDLERS
# --------------------------------------------------

@app.errorhandler(413)
def file_too_large(error):
    return "File too large. Maximum upload size is 20 MB.", 413


# --------------------------------------------------
# RUN APPLICATION
# --------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
