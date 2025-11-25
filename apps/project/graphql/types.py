import strawberry
import strawberry_django

from apps.project.models import Project
from apps.strategic.graphql.types import StrategicDirectivesType
from utils.graphql.types import DjangoFileType


@strawberry_django.type(Project)
class ProjectType:
    id: strawberry.ID
    title: strawberry.auto
    description: strawberry.auto
    cover_image: DjangoFileType
    strategic_directive: StrategicDirectivesType | None
    start_date: strawberry.auto
    end_date: strawberry.auto
