
import os
import uuid

# Store the AI model in Vercel's temporary writable directory
os.environ.setdefault("U2NET_HOME", "/tmp/.u2net")

from rembg import remove, new_session


session = None


def remove_background(image_path, result_folder):

    global session

    if not os.path.isfile(image_path):
        raise FileNotFoundError("Original image not found.")

    # Load the model only when background removal is requested
    if session is None:
        session = new_session("u2netp")

    os.makedirs(result_folder, exist_ok=True)

    with open(image_path, "rb") as input_file:
        input_data = input_file.read()

    output_data = remove(
        input_data,
        session=session
    )

    filename = f"background_removed_{uuid.uuid4().hex}.png"
    output_path = os.path.join(result_folder, filename)

    with open(output_path, "wb") as output_file:
        output_file.write(output_data)

    return filename