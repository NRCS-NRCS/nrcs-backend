import factory
from factory.django import DjangoModelFactory

from apps.users.tests.factory import UserFactory as UserFactory

from .models import MajorResponsibilities, StrategicDirectives


class StrategicDirectivesFactory(DjangoModelFactory):
    created_by = factory.SubFactory(UserFactory)
    modified_by = factory.SubFactory(UserFactory)

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        model = StrategicDirectives


class MajorResponsibilitiesFactory(DjangoModelFactory):
    created_by = factory.SubFactory(UserFactory)
    modified_by = factory.SubFactory(UserFactory)

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        model = MajorResponsibilities
