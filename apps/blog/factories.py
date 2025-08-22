import factory
from factory.django import DjangoModelFactory

# FIXME: Move this to user apps
from apps.strategic.factories import UserFactory

from .models import Blog


class BlogFactory(DjangoModelFactory):
    created_by = factory.SubFactory(UserFactory)
    modified_by = factory.SubFactory(UserFactory)

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        model = Blog
