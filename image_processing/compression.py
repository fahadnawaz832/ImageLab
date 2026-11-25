
import os
import uuid
from PIL import Image


def compress_image(image_path, result_folder, quality=75, output_format="JPEG"):

    quality = max(10, min(95, int(quality)))
    output_format = output_format.upper()

    if output_format not in ["JPEG", "WEBP"]:
        raise ValueError("Unsupported compression format.")

    os.makedirs(result_folder, exist_ok=True)

    original_size = os.path.getsize(image_path)

    with Image.open(image_path) as original:

        image = original.copy()

        if output_format == "JPEG":
            image = image.convert("RGB")

        filename = f"compressed_{uuid.uuid4().hex}.{output_format.lower()}"
        output_path = os.path.join(result_folder, filename)

        # Try progressively lower quality until file is smaller
        saved = False

        for current_quality in range(quality, 4, -5):

            image.save(
                output_path,
                format=output_format,
                quality=current_quality,
                optimize=True
            )

            if os.path.getsize(output_path) < original_size:
                saved = True
                break

        # If compression cannot reduce size, remove result
        if not saved:
            if os.path.exists(output_path):
                os.remove(output_path)

            raise ValueError(
                "This image is already highly optimized. "
                "Try another image or output format."
            )

    compressed_size = os.path.getsize(output_path)

    savings = ((original_size - compressed_size) / original_size) * 100

    return {
        "filename": filename,
        "original_size": original_size,
        "compressed_size": compressed_size,
        "savings": round(savings, 2)
    }
