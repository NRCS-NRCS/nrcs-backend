import strawberry
import strawberry_django

from .filters import BlogFilter
from .orders import BlogOrder
from .types import BlogType


@strawberry.type
class Query:
    blogs: list[BlogType] = strawberry_django.field(
        order=BlogOrder,
        filters=BlogFilter,
    )

    blog: BlogType = strawberry_django.field()
