import strawberry
import strawberry_django

from .filters import WorkFilter
from .orders import WorkOrder
from .types import WorkType


@strawberry.type
class Query:
    work: WorkType = strawberry_django.field()
    works: list[WorkType] = strawberry_django.field(
        order=WorkOrder,
        filters=WorkFilter,
    )
