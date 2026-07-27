import factory
from django.contrib.auth.models import User
from factory import fuzzy
from factory.django import DjangoModelFactory


class UserFactory(DjangoModelFactory):
    username = factory.Sequence(lambda n: f"user-{n}")
    email = factory.Sequence(lambda n: f"user-{n}@example.com")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        model = User

    @factory.post_generation
    def password(obj, create, password, **_):
        if not create:
            return
        password_text = password or fuzzy.FuzzyText(length=15).fuzz()
        obj.set_password(password_text)  # type: ignore[reportAttributeAccessIssue]
        obj.password_text = password_text
        obj.save()  # type: ignore[reportAttributeAccessIssue]
