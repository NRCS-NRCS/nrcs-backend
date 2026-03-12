# --- Move this to a common app later? --- #

import strawberry
import strawberry_django
from asgiref.sync import sync_to_async
from django.contrib.auth.models import User
from django.db import models
from strawberry_django.pagination import OffsetPaginated
from strawberry_django.permissions import IsAuthenticated

from main.graphql.context import Info

from .types import UserMeType, UserType


@strawberry.type
class Query:
    # Public --------------------
    @strawberry.field
    @sync_to_async
    def me(self, info: Info) -> UserMeType | None:
        user = info.context.request.user
        if user.is_authenticated:
            return user  # type: ignore[reportGeneralTypeIssues]
        return None

    # Private --------------------
    # --- Paginated
    @strawberry_django.offset_paginated(
        OffsetPaginated[UserType],
        extensions=[IsAuthenticated()],
    )
    def users(self) -> models.QuerySet[User]:
        return User.objects.filter(is_active=True)
