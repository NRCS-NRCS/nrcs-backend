import strawberry
import strawberry_django

from apps.department.graphql.types import DepartmentType
from apps.project.models import Project
from utils.graphql.types import DjangoFileType


@strawberry_django.type(Project)
class ProjectType:
    id: strawberry.ID
    title: strawberry.auto
    description: strawberry.auto
    cover_image: DjangoFileType
    department: DepartmentType | None
