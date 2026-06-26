import strawberry
import strawberry_django
from asgiref.sync import sync_to_async
from strawberry_django.permissions import IsAuthenticated, IsSuperuser

from apps.users.models import User
from apps.users.serializers import UserSerializer
from main.graphql.context import Info
from utils.graphql.drf import MutationCustomErrorType
from utils.graphql.mutations import ModelMutation
from utils.graphql.types import MutationResponseType

from .inputs import PasswordUpdateInput, UserCreateInput, UserUpdateInput
from .types import UserMeType, UserType


@strawberry.type
class Mutation:
    # Public --------------------
    login: UserMeType = strawberry_django.auth.login()  # type: ignore[reportAssignmentType]

    # Private --------------------
    logout = strawberry_django.auth.logout()

    @strawberry_django.mutation(extensions=[IsSuperuser()])
    async def create_user(
        self,
        info: Info,
        data: UserCreateInput,
    ) -> MutationResponseType[UserType]:
        return await ModelMutation(UserSerializer).handle_create_mutation(data, info)

    @strawberry_django.mutation(extensions=[IsSuperuser()])
    async def update_user(
        self,
        info: Info,
        id: strawberry.ID,
        data: UserUpdateInput,
    ) -> MutationResponseType[UserType]:
        instance = await User.objects.aget(id=id)
        return await ModelMutation(UserSerializer).handle_update_mutation(data, info, instance)

    @strawberry_django.mutation(extensions=[IsSuperuser()])
    async def delete_user(
        self,
        info: Info,
        id: strawberry.ID,
    ) -> MutationResponseType[UserType]:
        instance = await User.objects.aget(id=id)
        await instance.adelete()
        return MutationResponseType(ok=True)

    @strawberry_django.mutation(extensions=[IsSuperuser()])
    async def reset_user_password(
        self,
        info: Info,
        id: strawberry.ID,
        new_password: str,
    ) -> MutationResponseType[UserType]:
        instance = await User.objects.aget(id=id)
        await sync_to_async(instance.set_password)(new_password)
        await instance.asave()
        return MutationResponseType(result=instance)  # type: ignore[reportReturnType]

    @strawberry_django.mutation(extensions=[IsAuthenticated()])
    async def update_my_password(
        self,
        info: Info,
        data: PasswordUpdateInput,
    ) -> MutationResponseType[UserType]:
        user: User = info.context.request.user  # type: ignore[reportAssignmentType]
        password_valid = await sync_to_async(user.check_password)(data.current_password)
        if not password_valid:
            return MutationResponseType(
                ok=False,
                errors=MutationCustomErrorType.generate_message("Current password is incorrect."),
            )
        await sync_to_async(user.set_password)(data.new_password)
        await user.asave()
        return MutationResponseType(result=user)  # type: ignore[reportReturnType]
