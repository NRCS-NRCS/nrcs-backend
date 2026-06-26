import datetime
from enum import Enum

import strawberry
import strawberry_django
from asgiref.sync import sync_to_async
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
    first_name: strawberry.auto
    last_name: strawberry.auto
    is_active: strawberry.auto
    last_login: strawberry.auto

    @strawberry.field
    @sync_to_async
    def created_at(self) -> datetime.datetime:
        return self.date_joined  # type: ignore[reportAttributeAccessIssue]

    @strawberry.field
    @sync_to_async
    def user_type(self) -> UserTypeEnum:
        if self.is_superuser:  # type: ignore[reportAttributeAccessIssue]
            return UserTypeEnum.ADMIN
        if self.is_staff:  # type: ignore[reportAttributeAccessIssue]
            return UserTypeEnum.STAFF
        return UserTypeEnum.VIEWER


@strawberry_django.type(User)
class UserMeType(UserType):
    pass


@strawberry.interface
class UserResourceTypeMixin:
    created_at: datetime.datetime
    modified_at: datetime.datetime

    created_by: UserType
    modified_by: UserType
