import strawberry
import strawberry_django
from strawberry_django.pagination import OffsetPaginated

from .filters import MajorResponsibilitiesFilter, StrategicDirectivesFilter
from .orders import MajorResponsibilitiesOrder, StrategicDirectivesOrder
from .types import MajorResponsibilitiesType, StrategicDirectivesType


@strawberry.type
class Query:
    strategic_directives: OffsetPaginated[StrategicDirectivesType] = strawberry_django.offset_paginated(
        order=StrategicDirectivesOrder,
        filters=StrategicDirectivesFilter,
        extensions=[],
    )
    major_responsibilities: OffsetPaginated[MajorResponsibilitiesType] = strawberry_django.offset_paginated(
        order=MajorResponsibilitiesOrder,
        filters=MajorResponsibilitiesFilter,
        extensions=[],
    )
