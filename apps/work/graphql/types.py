import strawberry
import strawberry_django

from apps.department.graphql.types import DepartmentType
from apps.strategic.graphql.types import StrategicDirectivesType
from apps.work.models import Work


@strawberry_django.type(Work)
class WorkType:
    id: strawberry.ID
    title: strawberry.auto
    description: strawberry.auto
    cover_image: strawberry.auto
    department: DepartmentType
    strategic_directive: StrategicDirectivesType
    start_date: strawberry.auto
    end_date: strawberry.auto
