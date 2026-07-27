import strawberry
import strawberry_django
from django.contrib.auth.models import User

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


# --- Move this to a common app later? --- #


@strawberry_django.type(User)
class UserType:
    id: strawberry.ID
    first_name: strawberry.auto
    last_name: strawberry.auto


@strawberry_django.type(User)
class UserMeType(UserType):
    email: strawberry.auto
