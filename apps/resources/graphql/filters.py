import strawberry
import strawberry_django

from apps.resources.models import Resource, ResourcesType


@strawberry_django.filters.filter(Resource, lookups=True)
class ResourceFilter:
    name: str | None = strawberry.UNSET
    slug: str | None = strawberry.UNSET
    id: strawberry.ID | None = strawberry.UNSET
    directive: strawberry.ID | None = None
    type: ResourcesType | None = strawberry.UNSET
