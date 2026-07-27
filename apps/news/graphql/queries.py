import strawberry
import strawberry_django
from strawberry_django.pagination import OffsetPaginated

from .filters import NewsFilter
from .orders import NewsOrder
from .types import NewsType


@strawberry.type
class Query:
    # --- Paginated
    news: OffsetPaginated[NewsType] = strawberry_django.offset_paginated(
        order=NewsOrder,
        filters=NewsFilter,
    )
    news_item: NewsType = strawberry_django.field()
