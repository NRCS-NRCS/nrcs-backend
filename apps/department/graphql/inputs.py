import strawberry
import strawberry_django

from apps.department.models import Department


# NOTE: Make sure this matches with the serializers ../serializers.py
@strawberry_django.input(Department)
class DepartmentCreateInput:
    title: strawberry.auto
    description: strawberry.auto
    contact_person_name: strawberry.auto
    contact_person_email: strawberry.auto
    strategic_directive: strawberry.ID


@strawberry_django.partial(Department)
class DepartmentUpdateInput:
    title: strawberry.auto
    description: strawberry.auto
    contact_person_name: strawberry.auto
    contact_person_email: strawberry.auto
    strategic_directive: strawberry.ID


@strawberry_django.input(Department)
class DepartmentDeleteInput:
    id: strawberry.ID
