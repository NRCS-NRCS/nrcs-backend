import factory
from django.contrib.auth.models import User
from factory import fuzzy
from factory.django import DjangoModelFactory

from .models import MajorResponsibilities, StrategicDirectives


# TODO: Move this to user apps
class UserFactory(DjangoModelFactory):
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    username = factory.Sequence(lambda n: f"nrcs-{n}")

    class Meta:  # type: ignore[reportIncompatibleVariab]
        model = User

    @factory.post_generation
    def password(obj, create, password, **_):
        if not create:
            return
        password_text = password or fuzzy.FuzzyText(length=15).fuzz()
        obj.set_password(password_text)  # type: ignore[reportAttributeAccessIssue]
        obj.password_text = password_text
        obj.save()  # type: ignore[reportAttributeAccessIssue]


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
