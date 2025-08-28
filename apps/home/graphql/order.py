import strawberry
import strawberry_django

from apps.home.models import Highlight


@strawberry_django.ordering.order(Highlight)
class HighlightOrder:
    id: strawberry.auto
    heading: strawberry.auto
