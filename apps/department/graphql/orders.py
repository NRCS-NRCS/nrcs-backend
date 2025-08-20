import strawberry
import strawberry_django

from apps.department.models import Department


@strawberry_django.ordering.order(Department)
class DepartmentOrder:
    id: strawberry.auto
