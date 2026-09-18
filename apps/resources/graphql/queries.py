import strawberry
import strawberry_django
from strawberry_django.pagination import OffsetPaginated

from .filters import ResourceFilter
from .orders import ResourceOrder
from .types import ResourceType


@strawberry.type
class Query:
    # --- Paginated
    resources: OffsetPaginated[ResourceType] = strawberry_django.offset_paginated(
        order=ResourceOrder,
        filters=ResourceFilter,
    )
    resource: ResourceType = strawberry_django.field()
