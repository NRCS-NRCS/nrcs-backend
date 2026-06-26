import strawberry

from .types import UserTypeEnum


@strawberry.input
class UserCreateInput:
    email: str
    password: str
    first_name: str = ""
    last_name: str = ""
    user_type: UserTypeEnum = UserTypeEnum.VIEWER


@strawberry.input
class UserUpdateInput:
    email: str | None = strawberry.UNSET
    first_name: str | None = strawberry.UNSET
    last_name: str | None = strawberry.UNSET
    user_type: UserTypeEnum | None = strawberry.UNSET


@strawberry.input
class PasswordUpdateInput:
    current_password: str
    new_password: str
