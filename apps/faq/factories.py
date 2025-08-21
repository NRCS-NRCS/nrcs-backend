import factory
from factory.django import DjangoModelFactory

# FIXME
from apps.strategic.factories import UserFactory

from .models import Faq


class FaqFactory(DjangoModelFactory):
    created_by = factory.SubFactory(UserFactory)
    modified_by = factory.SubFactory(UserFactory)

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        model = Faq
