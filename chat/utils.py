"""Utility functions for image processing."""


from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile


def convert_image_to_webp(image):
    """Convert an uploaded image to WebP format."""

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
