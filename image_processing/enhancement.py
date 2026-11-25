
import cv2
import os


def enhance_image(
    image_path,
    output_path,
    brightness=0,
    contrast=1.0,
    rotation=0,
    width=None,
    height=None
):
    # Read original image
    image = cv2.imread(image_path)

    if image is None:
        raise ValueError("Unable to read input image.")

    # Brightness and Contrast
    brightness = max(-100, min(100, int(brightness)))
    contrast = max(0.1, min(3.0, float(contrast)))

    image = cv2.convertScaleAbs(
        image,
        alpha=contrast,
        beta=brightness
    )

    # Rotation
    if rotation == 90:
        image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)

    elif rotation == 180:
        image = cv2.rotate(image, cv2.ROTATE_180)

    elif rotation == 270:
        image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)

    elif rotation != 0:
        raise ValueError("Invalid rotation value.")

    # Resize
    if width and height:
        width = int(width)
        height = int(height)

        if not (1 <= width <= 5000 and 1 <= height <= 5000):
            raise ValueError("Width and height must be between 1 and 5000.")

        image = cv2.resize(
            image,
            (width, height),
            interpolation=cv2.INTER_AREA
        )

    # Save enhanced image
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    success = cv2.imwrite(output_path, image)

    if not success:
        raise ValueError("Unable to save enhanced image.")

    return output_path
