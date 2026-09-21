import strawberry
import strawberry_django
from strawberry_django.pagination import OffsetPaginated

from apps.department.graphql.orders import DepartmentOrder

from .filters import DepartmentFilter
from .types import DepartmentType


@strawberry.type
class Query:
    # --- Paginated
    departments: OffsetPaginated[DepartmentType] = strawberry_django.offset_paginated(
        order=DepartmentOrder,
        filters=DepartmentFilter,
    )

    # single department (by pk by default)
    department: DepartmentType = strawberry_django.field()
