
import cv2
import numpy as np


def generate_histogram(image_path):
    """Generate histogram according to uploaded image type."""

    image = cv2.imread(image_path)

    if image is None:
        raise ValueError("Unable to read image.")

    # Detect whether the image is grayscale
    is_grayscale = (
        np.array_equal(image[:, :, 0], image[:, :, 1])
        and np.array_equal(image[:, :, 1], image[:, :, 2])
    )

    histogram_data = {
        "is_grayscale": bool(is_grayscale)
    }

    if is_grayscale:

        # Generate only grayscale histogram
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        gray_hist = cv2.calcHist(
            [gray], [0], None, [256], [0, 256]
        )

        histogram_data["grayscale"] = gray_hist.flatten().tolist()

    else:

        # Generate only RGB histograms
        colors = ("b", "g", "r")

        for channel, color in enumerate(colors):

            hist = cv2.calcHist(
                [image], [channel], None, [256], [0, 256]
            )

            histogram_data[color] = hist.flatten().tolist()

    return histogram_data


def equalize_image(image_path, output_path):
    """Apply histogram equalization to an image."""

    image = cv2.imread(image_path)

    if image is None:
        raise ValueError("Unable to read image.")

    # Convert image to YCrCb color space
    ycrcb = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)

    # Equalize brightness channel
    ycrcb[:, :, 0] = cv2.equalizeHist(ycrcb[:, :, 0])

    # Convert back to BGR
    enhanced = cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2BGR)

    success = cv2.imwrite(output_path, enhanced)

    if not success:
        raise ValueError("Unable to save enhanced image.")

    return output_path
