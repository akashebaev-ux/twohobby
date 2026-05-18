from io import BytesIO
from django.core.files.base import ContentFile
from PIL import Image


def convert_image_to_webp(image):
    img = Image.open(image)

    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    output = BytesIO()

    img.save(
        output,
        format="WEBP",
        quality=80
    )

    original_name = image.name.rsplit(".", 1)[0]
    webp_name = f"{original_name}.webp"

    return ContentFile(
        output.getvalue(),
        name=webp_name
    )
