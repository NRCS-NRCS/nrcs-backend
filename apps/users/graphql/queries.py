import strawberry
import strawberry_django
from asgiref.sync import sync_to_async
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Case, CharField, Value, When
from django.db.models.functions import Concat
from strawberry_django.pagination import OffsetPaginated
from strawberry_django.permissions import IsAuthenticated

from main.graphql.context import Info

from .filters import UserFilter
from .types import UserMeType, UserType


def _annotate_users(qs: models.QuerySet[User]) -> models.QuerySet[User]:
    return qs.annotate(
        _user_type=Case(
            When(is_superuser=True, then=Value("admin")),
            When(is_staff=True, then=Value("staff")),
            default=Value("viewer"),
            output_field=CharField(),
        ),
        _full_name=Concat("first_name", Value(" "), "last_name"),
    )


@strawberry.type
class Query:
    @strawberry.field
    @sync_to_async
    def me(self, info: Info) -> UserMeType | None:
        user = info.context.request.user
        if user.is_authenticated:
            return _annotate_users(User.objects.filter(pk=user.pk)).first()
        return None

    @strawberry_django.offset_paginated(
        OffsetPaginated[UserType],
        extensions=[IsAuthenticated()],
        filters=UserFilter,
    )
    def users(self) -> models.QuerySet[User]:
        return _annotate_users(User.objects.filter(is_active=True))
