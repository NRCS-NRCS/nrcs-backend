import strawberry
import strawberry_django
from django.db.models import Q

from apps.strategic.models import MajorResponsibilities, StrategicDirectives


@strawberry_django.filters.filter(StrategicDirectives, lookups=True)
class StrategicDirectivesFilter:
    slug: strawberry.auto
    id: strawberry.ID | None = strawberry.UNSET

    @strawberry_django.filter_field
    def search(self, value: str, prefix: str) -> Q:
        return Q(title__icontains=value)


@strawberry_django.filters.filter(MajorResponsibilities, lookups=True)
class MajorResponsibilitiesFilter:
    slug: strawberry.auto
    directive: strawberry.auto
    id: strawberry.ID | None = strawberry.UNSET

    @strawberry_django.filter_field
    def search(self, value: str, prefix: str) -> Q:
        return Q(title__icontains=value)
