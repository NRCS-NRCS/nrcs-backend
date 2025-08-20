import strawberry
import strawberry_django
from strawberry_django.pagination import OffsetPaginated

from .filters import ProcurementFilter
from .orders import ProcurementOrder
from .types import ProcurementType


@strawberry.type
class Query:
    procurement: OffsetPaginated[ProcurementType] = strawberry_django.offset_paginated(
        order=ProcurementOrder,
        filters=ProcurementFilter,
        extensions=[],
    )
