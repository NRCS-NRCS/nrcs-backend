import strawberry
import strawberry_django
from django.contrib.auth import get_user_model

from .types import UserTypeEnum

User = get_user_model()


@strawberry_django.input(User)
class UserCreateInput:
    email: str
    password: str
    first_name: str
    last_name: str
    username: str
    user_type: UserTypeEnum = UserTypeEnum.VIEWER
    is_active: bool | None = strawberry.UNSET


@strawberry_django.partial(User)
class UserUpdateInput:
    id: strawberry.ID
    email: str | None = strawberry.UNSET
    first_name: str | None = strawberry.UNSET
    last_name: str | None = strawberry.UNSET
    username: str | None = strawberry.UNSET
    user_type: UserTypeEnum | None = strawberry.UNSET
    is_active: bool | None = strawberry.UNSET


@strawberry.input
class PasswordUpdateInput:
    current_password: str
    new_password: str


@strawberry.input
class UserDeleteInput:
    id: strawberry.ID


@strawberry.input
class PasswordResetInput:
    id: strawberry.ID
