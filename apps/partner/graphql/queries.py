import strawberry
import strawberry_django
from strawberry_django.pagination import OffsetPaginated

from .filters import PartnerFilter
from .orders import PartnerOrder
from .types import PartnerType


@strawberry.type
class Query:
    # --- Paginated
    partners: OffsetPaginated[PartnerType] = strawberry_django.offset_paginated(
        order=PartnerOrder,
        filters=PartnerFilter,
    )
    partner: PartnerType = strawberry_django.field()
