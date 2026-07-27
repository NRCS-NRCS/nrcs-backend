import strawberry
import strawberry_django
from strawberry_django.pagination import OffsetPaginated

from .filters import ProjectFilter
from .orders import ProjectOrder
from .types import ProjectType


@strawberry.type
class Query:
    project: ProjectType = strawberry_django.field()

    # --- Paginated
    projects: OffsetPaginated[ProjectType] = strawberry_django.offset_paginated(
        order=ProjectOrder,
        filters=ProjectFilter,
    )
