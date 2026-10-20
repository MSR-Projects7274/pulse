from django.core.exceptions import ValidationError


# Limit uploaded images before storage to prevent oversized media files.
MAX_IMAGE_SIZE = 5 * 1024 * 1024


# Django calls this validator whenever an uploaded Post image is validated.
def validate_image_size(image):
    if image.size > MAX_IMAGE_SIZE:
        raise ValidationError(
            "Image file size must be 5 MB or less."
        )
