import strawberry
import strawberry_django

from .filters import PartnerFilter
from .orders import PartnerOrder
from .types import PartnerType


@strawberry.type
class Query:
    partners: list[PartnerType] = strawberry_django.field(
        order=PartnerOrder,
        filters=PartnerFilter,
    )
    partner: PartnerType = strawberry_django.field()
