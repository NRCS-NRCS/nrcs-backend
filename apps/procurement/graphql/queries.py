import strawberry
import strawberry_django

from .filters import ProcurementFilter
from .orders import ProcurementOrder
from .types import ProcurementType


@strawberry.type
class Query:
    procurements: list[ProcurementType] = strawberry_django.field(
        order=ProcurementOrder,
        filters=ProcurementFilter,
    )
    procurement: ProcurementType = strawberry_django.field()
