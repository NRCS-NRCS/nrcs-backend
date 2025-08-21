import strawberry
import strawberry_django

from apps.resources.models import Resource


@strawberry_django.filters.filter(Resource, lookups=True)
class ResourceFilter:
    name: str | None = strawberry.UNSET
