import strawberry

from .types import UserTypeEnum


@strawberry.input
class CreateUserInput:
    email: str
    full_name: str
    password: str
    user_type: UserTypeEnum = UserTypeEnum.VIEWER


@strawberry.input
class UpdateUserInput:
    email: str | None = strawberry.UNSET
    full_name: str | None = strawberry.UNSET
    password: str | None = strawberry.UNSET
    user_type: UserTypeEnum | None = strawberry.UNSET
