import strawberry
import strawberry_django
from strawberry_django.pagination import OffsetPaginated

from .filters import RadioProgramFilter
from .orders import RadioProgramOrder
from .types import RadioProgramType


@strawberry.type
class Query:
    # --- Paginated
    radio_program: OffsetPaginated[RadioProgramType] = strawberry_django.offset_paginated(
        order=RadioProgramOrder,
        filters=RadioProgramFilter,
    )
