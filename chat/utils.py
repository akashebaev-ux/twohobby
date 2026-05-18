from io import BytesIO

from django.core.files.base import ContentFile
from PIL import Image


def convert_image_to_webp(image_file):
    image = Image.open(image_file)

    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")

    output = BytesIO()

    image.save(
        output,
        format="WEBP",
        quality=75,
        optimize=True
    )

    output.seek(0)

    original_name = image_file.name.rsplit(".", 1)[0]

    return ContentFile(
        output.read(),
        name=f"{original_name}.webp"
    )
