import strawberry
import strawberry_django

from apps.department.graphql.types import DepartmentType
from apps.strategic.graphql.types import StrategicDirectivesType
from apps.work.models import Work
from utils.graphql.types import DjangoFileType


@strawberry_django.type(Work)
class WorkType:
    id: strawberry.ID
    title: strawberry.auto
    description: strawberry.auto
    cover_image: DjangoFileType
    department: DepartmentType
    strategic_directive: StrategicDirectivesType | None
    start_date: strawberry.auto
    end_date: strawberry.auto
