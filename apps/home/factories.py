import factory
from factory.django import DjangoModelFactory

from apps.strategic.factories import UserFactory

from .models import ActionLink, Highlight, KeyStat


class HighlightFactory(DjangoModelFactory):
    created_by = factory.SubFactory(UserFactory)
    modified_by = factory.SubFactory(UserFactory)

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        model = Highlight


class ActionLinkFactory(DjangoModelFactory):
    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        model = ActionLink


class KeyStatFactory(DjangoModelFactory):
    order = factory.Sequence(lambda n: n + 1)
    title = factory.Sequence(lambda n: f"Key Stat {n}")
    stat = factory.Sequence(lambda n: n + 1)

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        model = KeyStat
