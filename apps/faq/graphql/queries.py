import strawberry
import strawberry_django
from strawberry_django.pagination import OffsetPaginated

from .filters import FaqFilter
from .orders import FaqOrder
from .types import FaqType


@strawberry.type
class Query:
    # --- Paginated
    faqs: OffsetPaginated[FaqType] = strawberry_django.offset_paginated(
        order=FaqOrder,
        filters=FaqFilter,
    )
    faq: FaqType = strawberry_django.field()
