import strawberry
import strawberry_django

from .filters import MajorResponsibilitiesFilter, StrategicDirectivesFilter
from .orders import MajorResponsibilitiesOrder, StrategicDirectivesOrder
from .types import MajorResponsibilitiesType, StrategicDirectivesType


@strawberry.type
class Query:
    strategic_directives: list[StrategicDirectivesType] = strawberry_django.field(
        order=StrategicDirectivesOrder,
        filters=StrategicDirectivesFilter,
    )
    strategic_directive: StrategicDirectivesType = strawberry_django.field()

    major_responsibilities: list[MajorResponsibilitiesType] = strawberry_django.field(
        order=MajorResponsibilitiesOrder,
        filters=MajorResponsibilitiesFilter,
    )
    major_responsibility: MajorResponsibilitiesType = strawberry_django.field()
