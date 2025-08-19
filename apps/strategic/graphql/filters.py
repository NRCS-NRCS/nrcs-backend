import strawberry
import strawberry_django

from apps.strategic.models import MajorResponsibilities, StrategicDirectives


@strawberry_django.filters.filter(StrategicDirectives, lookups=True)
class StrategicDirectivesFilter:
    id: strawberry.auto
    slug: strawberry.auto


@strawberry_django.filters.filter(MajorResponsibilities, lookups=True)
class MajorResponsibilitiesFilter:
    id: strawberry.auto
    slug: strawberry.auto
    directive: strawberry.auto
