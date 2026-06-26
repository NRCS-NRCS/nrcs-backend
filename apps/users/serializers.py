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


class UserSerializer(serializers.ModelSerializer[User]):
    user_type = EnumCharField(write_only=True, required=False, default="viewer")

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "password", "user_type"]
        extra_kwargs = {"password": {"write_only": True, "required": False}}

    @typing.override
    def create(self, validated_data: dict[str, typing.Any]) -> User:
        user_type = validated_data.pop("user_type", "viewer")
        password = validated_data.pop("password", None)
        user = User.objects.create_user(username=validated_data["email"], password=password or "", **validated_data)
        _apply_user_type(user, user_type)
        user.save(update_fields=["is_staff", "is_superuser"])
        return user

    @typing.override
    def update(self, instance: User, validated_data: dict[str, typing.Any]) -> User:
        validated_data.pop("password", None)
        user_type = validated_data.pop("user_type", None)
        instance = super().update(instance, validated_data)
        if user_type is not None:
            _apply_user_type(instance, user_type)
            instance.save(update_fields=["is_staff", "is_superuser"])
        return instance
