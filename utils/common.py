import copy
from typing import TypeVar

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


T = TypeVar("T", bound=Model)


def unique_slugify(instance: T, slug: str) -> str:
    model = instance.__class__
    unique_slug = slug
    while model.objects.filter(slug=unique_slug).exists():
        unique_slug = slug + get_random_string(length=4)
    return unique_slug
