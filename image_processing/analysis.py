
import os
import cv2
import numpy as np

from PIL import Image


def analyze_image(image_path):

    if not os.path.exists(image_path):
        raise FileNotFoundError("Image file not found.")

    # Read image using Pillow
    with Image.open(image_path) as image:

        width, height = image.size
        image_format = image.format or "Unknown"
        color_mode = image.mode

        # Convert to RGB for consistent analysis
        rgb_image = image.convert("RGB")
        image_array = np.array(rgb_image)

    # File size
    file_size_bytes = os.path.getsize(image_path)

    if file_size_bytes < 1024 * 1024:
        file_size = f"{file_size_bytes / 1024:.2f} KB"
    else:
        file_size = f"{file_size_bytes / (1024 * 1024):.2f} MB"

    # Total pixels
    total_pixels = width * height

    # Detect grayscale or color
    if color_mode in ("1", "L", "I", "I;16"):
        image_type = "Grayscale"
        channels = 1
    elif color_mode == "LA":
        image_type = "Grayscale with Alpha"
        channels = 2
    elif color_mode == "RGBA":
        image_type = "Color (RGBA)"
        channels = 4
    else:
        image_type = "Color (RGB)"
        channels = 3

    # OpenCV image information
    cv_image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)

    if cv_image is None:
        raise ValueError("Unable to read image.")

    return {
        "width": width,
        "height": height,
        "dimensions": f"{width} × {height}",
        "total_pixels": f"{total_pixels:,}",
        "format": image_format.upper(),
        "file_size": file_size,
        "file_size_bytes": file_size_bytes,
        "image_type": image_type,
        "channels": channels,
        "color_mode": color_mode,
        "array_shape": str(image_array.shape),
        "dtype": str(image_array.dtype)
    }
