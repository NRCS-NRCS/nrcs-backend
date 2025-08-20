import strawberry
import strawberry_django

from apps.department.graphql.orders import DepartmentOrder

from .filters import DepartmentFilter
from .types import DepartmentType


@strawberry.type
class Query:
    # all departments (no pagination)
    departments: list[DepartmentType] = strawberry_django.field(
        order=DepartmentOrder,
        filters=DepartmentFilter,
    )

    # single department (by pk by default)
    department: DepartmentType = strawberry_django.field()
