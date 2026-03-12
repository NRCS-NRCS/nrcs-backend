import strawberry
import strawberry_django
from strawberry_django.pagination import OffsetPaginated

from .filters import HighlightFilter
from .order import HighlightOrder
from .types import HighlightType


@strawberry.type
class Query:
    # --- Paginated
    highlights: OffsetPaginated[HighlightType] = strawberry_django.offset_paginated(
        filters=HighlightFilter,
        order=HighlightOrder,
    )
    highlight: HighlightType = strawberry_django.field()
