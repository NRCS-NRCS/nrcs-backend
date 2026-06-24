import datetime
from enum import Enum

import strawberry
import strawberry_django
from django.contrib.auth.models import User


@strawberry.enum
class UserTypeEnum(Enum):
    VIEWER = "viewer"
    STAFF = "staff"
    ADMIN = "admin"


@strawberry_django.type(User)
class UserType:
    id: strawberry.ID
    email: strawberry.auto
    is_active: strawberry.auto

    @strawberry.field
    def full_name(self) -> str:
        return self.__dict__.get("_full_name", "").strip() or self.__dict__.get("email", "")  # type: ignore[reportAttributeAccessIssue]

    @strawberry.field
    def user_type(self) -> UserTypeEnum:
        return UserTypeEnum(self.__dict__.get("_user_type", "viewer"))


@strawberry_django.type(User)
class UserMeType(UserType):
    last_login: strawberry.auto

    @strawberry.field
    def created_at(self) -> datetime.datetime:
        return self.__dict__.get("date_joined") or self.date_joined  # type: ignore[reportAttributeAccessIssue]


@strawberry.interface
class UserResourceTypeMixin:
    created_at: datetime.datetime
    modified_at: datetime.datetime

    created_by: UserType
    modified_by: UserType
