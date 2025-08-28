import strawberry
import strawberry_django

from .filters import HighlightFilter
from .order import HighlightOrder
from .types import HighlightType


@strawberry.type
class Query:
    highlights: list[HighlightType] = strawberry_django.field(
        filters=HighlightFilter,
        order=HighlightOrder,
    )
    highlight: HighlightType = strawberry_django.field()
