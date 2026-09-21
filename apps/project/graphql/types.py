import strawberry
import strawberry_django

from apps.common.graphql.types import UserResourceTypeMixin
from apps.department.graphql.types import DepartmentType
from apps.project.models import Project
from utils.graphql.types import DjangoFileType


@strawberry_django.type(Project)
class ProjectType(UserResourceTypeMixin):
    id: strawberry.ID
    title: strawberry.auto
    description: strawberry.auto
    cover_image: DjangoFileType
    department: DepartmentType | None
