import factory
from factory.django import DjangoModelFactory

# FIXME: Move this to user apps
from apps.strategic.factories import UserFactory

from .models import Department


class DepartmentFactory(DjangoModelFactory):
    created_by = factory.SubFactory(UserFactory)
    modified_by = factory.SubFactory(UserFactory)

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        model = Department
