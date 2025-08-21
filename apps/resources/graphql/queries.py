import strawberry
import strawberry_django

from .filters import ResourceFilter
from .orders import ResourceOrder
from .types import ResourceType


@strawberry.type
class Query:
    resources: list[ResourceType] = strawberry_django.field(
        order=ResourceOrder,
        filters=ResourceFilter,
    )
    resource: ResourceType = strawberry_django.field()
