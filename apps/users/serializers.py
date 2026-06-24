import typing

from django.contrib.auth.models import User
from rest_framework import serializers


class EnumCharField(serializers.CharField):
    def to_internal_value(self, data: typing.Any) -> str:
        if hasattr(data, "value"):
            data = data.value
        return super().to_internal_value(data)


def _apply_user_type(user: User, user_type: str) -> None:
    user.is_staff = user_type in ("staff", "admin")
    user.is_superuser = user_type == "admin"


class UserCreateSerializer(serializers.ModelSerializer[User]):
    full_name = serializers.CharField(write_only=True, required=False, default="")
    user_type = EnumCharField(write_only=True, required=False, default="viewer")

    class Meta:
        model = User
        fields = ["email", "full_name", "password", "user_type"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate_email(self, value: str) -> str:
        if value and User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with that email already exists.")
        return value

    @typing.override
    def create(self, validated_data: dict[str, typing.Any]) -> User:
        user_type = validated_data.pop("user_type", "viewer")
        full_name = validated_data.pop("full_name", "")
        password = validated_data.pop("password")
        email = validated_data["email"]

        base_username = email.split("@")[0]
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        user = User(username=username, first_name=full_name, **validated_data)
        user.set_password(password)
        _apply_user_type(user, user_type)
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer[User]):
    full_name = serializers.CharField(write_only=True, required=False)
    user_type = EnumCharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ["email", "full_name", "password", "user_type"]
        extra_kwargs = {"password": {"write_only": True, "required": False}}

    def validate_email(self, value: str) -> str:
        if not value:
            return value
        qs = User.objects.filter(email=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("A user with that email already exists.")
        return value

    @typing.override
    def update(self, instance: User, validated_data: dict[str, typing.Any]) -> User:
        password = validated_data.pop("password", None)
        user_type = validated_data.pop("user_type", None)
        full_name = validated_data.pop("full_name", None)

        instance = super().update(instance, validated_data)

        if full_name is not None:
            instance.first_name = full_name
            instance.save(update_fields=["first_name"])

        if password:
            instance.set_password(password)
            instance.save()

        if user_type is not None:
            _apply_user_type(instance, user_type)
            instance.save(update_fields=["is_staff", "is_superuser"])

        return instance
