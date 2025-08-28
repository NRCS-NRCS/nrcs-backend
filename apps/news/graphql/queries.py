import strawberry
import strawberry_django

from .filters import NewsFilter
from .orders import NewsOrder
from .types import NewsType


@strawberry.type
class Query:
    news: list[NewsType] = strawberry_django.field(
        order=NewsOrder,
        filters=NewsFilter,
    )
    news_item: NewsType = strawberry_django.field()
