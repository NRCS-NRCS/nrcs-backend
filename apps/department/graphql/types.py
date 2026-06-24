import strawberry
import strawberry_django

from apps.common.graphql.types import UserResourceTypeMixin
from apps.department.models import Department
from apps.strategic.graphql.types import StrategicDirectivesType


@strawberry_django.type(Department)
class DepartmentType(UserResourceTypeMixin):
    id: strawberry.ID
    title: strawberry.auto
    description: strawberry.auto
    contact_person_name: strawberry.auto
    contact_person_email: strawberry.auto
    slug: strawberry.auto
    strategic_directive_id: strawberry.ID | None
    strategic_directive: StrategicDirectivesType | None
