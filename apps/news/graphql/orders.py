import strawberry
import strawberry_django

from apps.news.models import News


@strawberry_django.order_type(News)
class NewsOrder:
    id: strawberry.auto
    title: strawberry.auto
    status: strawberry.auto
    published_date: strawberry.auto
