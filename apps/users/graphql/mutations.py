import strawberry
import strawberry_django
from django.contrib.auth.models import User
from django.db.models import Case, CharField, Value, When
from django.db.models.functions import Concat
from strawberry_django.auth.mutations import resolve_login, resolve_logout
from strawberry_django.permissions import IsAuthenticated
from strawberry_django.resolvers import django_resolver

from apps.users.serializers import UserCreateSerializer, UserUpdateSerializer
from main.graphql.context import Info
from utils.graphql.mutations import ModelMutation
from utils.graphql.types import MutationResponseType

from .inputs import CreateUserInput, UpdateUserInput
from .types import UserMeType, UserType


def _annotate_user(user: User) -> User | None:
    return (
        User.objects.filter(pk=user.pk)
        .annotate(
            _user_type=Case(
                When(is_superuser=True, then=Value("admin")),
                When(is_staff=True, then=Value("staff")),
                default=Value("viewer"),
                output_field=CharField(),
            ),
            _full_name=Concat("first_name", Value(" "), "last_name"),
        )
        .first()
    )


@strawberry.type
class Mutation:
    @strawberry.mutation
    @django_resolver
    def login(self, info: Info, email: str, password: str) -> UserMeType:
        try:
            user_obj = User.objects.get(email=email)
            username = user_obj.username
        except User.DoesNotExist:
            username = email
        logged_in = resolve_login(info, username=username, password=password)  # type: ignore[reportReturnType]
        return _annotate_user(logged_in)  # type: ignore[reportReturnType]

    @strawberry.mutation
    @django_resolver
    def logout(self, info: Info) -> bool:
        return resolve_logout(info)  # type: ignore[reportReturnType]

    @strawberry_django.mutation(extensions=[IsAuthenticated()])
    async def create_user(self, info: Info, data: CreateUserInput) -> MutationResponseType[UserType]:
        if not info.context.request.user.is_superuser:
            return MutationResponseType(
                ok=False,
                errors=[{"field": "nonFieldErrors", "messages": ["Only admin users can create users."]}],
                result=None,
            )
        return await ModelMutation(UserCreateSerializer).handle_create_mutation(data, info, None)

    @strawberry_django.mutation(extensions=[IsAuthenticated()])
    async def update_user(
        self,
        info: Info,
        data: UpdateUserInput,
        pk: strawberry.ID,
    ) -> MutationResponseType[UserType]:
        requesting_user = info.context.request.user
        target_user = await User.objects.aget(pk=pk)
        if not requesting_user.is_staff and requesting_user.pk != target_user.pk:
            return MutationResponseType(
                ok=False,
                errors=[{"field": "nonFieldErrors", "messages": ["You do not have permission to update this user."]}],
                result=None,
            )
        return await ModelMutation(UserUpdateSerializer).handle_update_mutation(data, info, target_user)

    @strawberry_django.mutation(extensions=[IsAuthenticated()])
    async def delete_user(self, info: Info, pk: strawberry.ID) -> MutationResponseType[UserType]:
        requesting_user = info.context.request.user
        if not requesting_user.is_staff:
            return MutationResponseType(
                ok=False,
                errors=[{"field": "nonFieldErrors", "messages": ["Only admin users can delete users."]}],
                result=None,
            )
        user = await User.objects.aget(pk=pk)
        user.is_active = False
        await user.asave()
        return MutationResponseType(ok=True, errors=None, result=user)
