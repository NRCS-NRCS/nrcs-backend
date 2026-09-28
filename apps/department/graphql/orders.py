import strawberry
import strawberry_django

from apps.department.models import Department


@strawberry_django.order_type(Department)
class DepartmentOrder:
    id: strawberry.auto
