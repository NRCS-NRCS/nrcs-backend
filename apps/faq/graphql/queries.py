import strawberry
import strawberry_django

from .filters import FaqFilter
from .orders import FaqOrder
from .types import FaqType


@strawberry.type
class Query:
    faqs: list[FaqType] = strawberry_django.field(
        order=FaqOrder,
        filters=FaqFilter,
    )
    faq: FaqType = strawberry_django.field()
