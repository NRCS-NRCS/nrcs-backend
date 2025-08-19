import strawberry
import strawberry_django

from apps.strategic.models import MajorResponsibilities, StrategicDirectives


@strawberry_django.ordering.order(StrategicDirectives)
class StrategicDirectivesOrder:
    id: strawberry.auto


@strawberry_django.ordering.order(MajorResponsibilities)
class MajorResponsibilitiesOrder:
    id: strawberry.auto
    directive: strawberry.auto
