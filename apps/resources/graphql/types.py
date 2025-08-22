import strawberry
import strawberry_django

from apps.resources.models import Resource
from utils.graphql.types import DjangoFileType


@strawberry_django.type(Resource)
class ResourceType:
    id: strawberry.ID
    title: strawberry.auto
    file: DjangoFileType
    content: str
    published_date: strawberry.auto
