import strawberry
import strawberry_django

from apps.resources.models import Resource


@strawberry_django.type(Resource)
class ResourceType:
    id: strawberry.ID
    title: strawberry.auto
    file: strawberry.auto
    content: str
    published_date: strawberry.auto
