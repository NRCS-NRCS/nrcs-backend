import strawberry
import strawberry_django

from apps.blog.models import Blog


@strawberry_django.ordering.order(Blog)
class BlogOrder:
    id: strawberry.auto
    featured: strawberry.auto
