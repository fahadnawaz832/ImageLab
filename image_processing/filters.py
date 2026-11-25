
import cv2
import numpy as np


def apply_filter(image_path, output_path, filter_type, intensity=1):

    image = cv2.imread(image_path)

    if image is None:
        raise ValueError("Unable to read image.")

    if filter_type == "grayscale":
        processed = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    elif filter_type == "gaussian":
        processed = cv2.GaussianBlur(image, (15, 15), 0)

    elif filter_type == "median":
        processed = cv2.medianBlur(image, 5)

    elif filter_type == "edge":
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        processed = cv2.Canny(gray, 100, 200)

    elif filter_type == "sharpen":
        kernel = np.array([
            [0, -1, 0],
            [-1, 5, -1],
            [0, -1, 0]
        ])
        processed = cv2.filter2D(image, -1, kernel)

    elif filter_type == "brightness":
        brightness = max(-100, min(100, int(intensity)))
        processed = cv2.convertScaleAbs(
            image, alpha=1.0, beta=brightness
        )

    elif filter_type == "contrast":
        contrast = max(0.5, min(2.0, float(intensity)))
        processed = cv2.convertScaleAbs(
            image, alpha=contrast, beta=0
        )

    else:
        raise ValueError("Unknown filter type.")

    success = cv2.imwrite(output_path, processed)

    if not success:
        raise ValueError("Unable to save processed image.")

    return output_path