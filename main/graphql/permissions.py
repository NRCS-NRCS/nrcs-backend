import typing

from strawberry.permission import BasePermission
from strawberry.types import Info


class IsAuthenticated(BasePermission):
    message = "User is not authenticated"

    def has_permission(self, source: typing.Any, info: Info, **_) -> bool:
        user = info.context.request.user
        return bool(user and user.is_authenticated)


class IsSuperAdmin(BasePermission):
    message = "User is not a superuser"

    def has_permission(self, source: typing.Any, info: Info, **_) -> bool:
        user = info.context.request.user
        return bool(user and user.is_authenticated and user.is_superuser)
