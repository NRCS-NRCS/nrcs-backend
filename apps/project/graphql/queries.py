import strawberry
import strawberry_django

from .filters import ProjectFilter
from .orders import ProjectOrder
from .types import ProjectType


@strawberry.type
class Query:
    project: ProjectType = strawberry_django.field()
    projects: list[ProjectType] = strawberry_django.field(
        order=ProjectOrder,
        filters=ProjectFilter,
    )
