import strawberry
import strawberry_django

from apps.home.models import Highlight


@strawberry_django.filters.filter(Highlight, lookups=True)
class HighlightFilter:
    expiry_date: strawberry.auto
    heading: strawberry.auto
