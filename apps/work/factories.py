import factory
from factory.django import DjangoModelFactory

from apps.strategic.factories import UserFactory

from .models import Work


class WorkFactory(DjangoModelFactory):
    created_by = factory.SubFactory(UserFactory)
    modified_by = factory.SubFactory(UserFactory)

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        model = Work
