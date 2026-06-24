import strawberry
import strawberry_django
from django.db.models import Q

from apps.resources.models import Resource, ResourceTypeEnum


@strawberry_django.filters.filter(Resource, lookups=True)
class ResourceFilter:
    name: str | None = strawberry.UNSET
    slug: str | None = strawberry.UNSET
    id: strawberry.ID | None = strawberry.UNSET
    directive: strawberry.ID | None = None
    type: ResourceTypeEnum | None = strawberry.UNSET
    search: str | None = strawberry.UNSET

    @strawberry_django.filter_field
    def search(self, value: str, prefix: str) -> Q:
        return Q(title__icontains=value)
