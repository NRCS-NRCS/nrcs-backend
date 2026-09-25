import factory
from factory.django import DjangoModelFactory

from apps.strategic.factories import UserFactory

from .models import CecMember


class CecMemberFactory(DjangoModelFactory):
    name = factory.Sequence(lambda n: f"Member {n}")
    created_by = factory.SubFactory(UserFactory)
    modified_by = factory.SubFactory(UserFactory)

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        model = CecMember
