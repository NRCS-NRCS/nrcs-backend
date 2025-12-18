import strawberry
import strawberry_django

from apps.home.models import Highlight


@strawberry_django.filters.filter(Highlight, lookups=True)
class HighlightFilter:
    heading: str | None = None
    is_active: bool | None = strawberry.UNSET
