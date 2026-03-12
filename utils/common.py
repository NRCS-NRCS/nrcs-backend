import copy

from django.core.exceptions import ValidationError
from django.core.files import File
from django.db.models import Model
from django.utils.crypto import get_random_string


def clean_up_none_keys(data):
    """
    Remove keys with none values (Also supports nested dict)
    Input:
     {"a": None, "b": "Hi"}
    Output:
     {"b": "Hi"}
    """
    _clone_data = copy.deepcopy(data)
    for key, value in data.items():
        if value is None:
            _clone_data.pop(key)
        if isinstance(value, dict):
            _clone_data[key] = clean_up_none_keys(value)
    return _clone_data


def unique_slugify(instance: Model, slug: str) -> str:
    model = instance.__class__
    unique_slug = slug
    while model.objects.filter(slug=unique_slug).exists():
        unique_slug = slug + get_random_string(length=4)
    return unique_slug


MAX_IMAGE_FILE_SIZE = 4
MAX_FILE_SIZE = 7
MAX_RADIO_PROGRAM_FILE_SIZE = 40


def validate_file_size(file: File, max_size: int) -> None:
    """
    This function validates that a given uploaded file does not exceed
    the specified size limit.

    Args:
        file: The uploaded file to validate.
        max_size: Maximum allowed file size in megabytes.

    Raises:
        ValidationError: If the file size exceeds the allowed limit.
    """
    max_size_bytes = max_size * 1024 * 1024  # Convert to MB

    if file.size > max_size_bytes:
        raise ValidationError(
            f"File is too large. Max file size must be less than {max_size} MB.",
        )
