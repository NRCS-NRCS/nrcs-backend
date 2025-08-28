import strawberry
import strawberry_django

from apps.news.models import News


@strawberry_django.ordering.order(News)
class NewsOrder:
    id: strawberry.auto
    title: strawberry.auto
    status: strawberry.auto
    published_date: strawberry.auto
