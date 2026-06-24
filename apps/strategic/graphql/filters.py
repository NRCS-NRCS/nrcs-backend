import strawberry
import strawberry_django
from django.db.models import Q

from apps.strategic.models import MajorResponsibilities, StrategicDirectives


@strawberry_django.filters.filter(StrategicDirectives, lookups=True)
class StrategicDirectivesFilter:
    id: strawberry.ID
    slug: strawberry.auto
    search: str | None = strawberry.UNSET

    @strawberry_django.filter_field
    def search(self, value: str, prefix: str) -> Q:
        return Q(title__icontains=value)


@strawberry_django.filters.filter(MajorResponsibilities, lookups=True)
class MajorResponsibilitiesFilter:
    id: strawberry.ID
    slug: strawberry.auto
    directive: strawberry.auto
    search: str | None = strawberry.UNSET

    @strawberry_django.filter_field
    def search(self, value: str, prefix: str) -> Q:
        return Q(title__icontains=value)
