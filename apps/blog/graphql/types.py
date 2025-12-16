import strawberry
import strawberry_django

from apps.blog.models import Blog
from apps.common.graphql.types import UserResourceTypeMixin
from apps.department.graphql.types import DepartmentType
from apps.strategic.graphql.types import StrategicDirectivesType
from utils.graphql.types import DjangoFileType


@strawberry_django.type(Blog)
class BlogType(UserResourceTypeMixin):
    id: strawberry.ID
    title: strawberry.auto
    published_date: strawberry.auto
    author: strawberry.auto
    content: str
    cover_image: DjangoFileType | None
    featured: strawberry.auto
    status: strawberry.auto
    slug: strawberry.auto
    department_id: strawberry.ID | None
    directive_id: strawberry.ID | None
    department: DepartmentType | None
    directive: StrategicDirectivesType | None
