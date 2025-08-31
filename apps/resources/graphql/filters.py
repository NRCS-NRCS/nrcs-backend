import strawberry
import strawberry_django

from apps.resources.models import Resource
from apps.strategic.graphql.types import StrategicDirectivesType


@strawberry_django.filters.filter(Resource, lookups=True)
class ResourceFilter:
    name: str | None = strawberry.UNSET
    slug: str | None = strawberry.UNSET
    id: strawberry.ID | None = strawberry.UNSET
    directive: StrategicDirectivesType | None = strawberry.UNSET
