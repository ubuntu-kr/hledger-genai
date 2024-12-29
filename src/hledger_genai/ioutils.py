import base64
def image_to_base64(file_path: str):
    with open(file_path, "rb") as file:
        base64_image = base64.b64encode(file.read()).decode("utf-8")

    file_ext = file_path.split(".")[-1]  # jpg
    return f"data:image/{file_ext};base64,{base64_image}"

