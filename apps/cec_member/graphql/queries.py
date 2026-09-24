import strawberry
import strawberry_django
from strawberry_django.pagination import OffsetPaginated

from .filters import CecMemberFilter
from .orders import CecMemberOrder
from .types import CecMemberType


@strawberry.type
class Query:
    # --- Paginated
    cec_members: OffsetPaginated[CecMemberType] = strawberry_django.offset_paginated(
        order=CecMemberOrder,
        filters=CecMemberFilter,
    )
    cec_member: CecMemberType = strawberry_django.field()
