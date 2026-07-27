import strawberry
import strawberry_django
from strawberry.file_uploads import Upload

from apps.resources.models import Resource


@strawberry_django.input(Resource)
class ResourceCreateInput:
    title: strawberry.auto
    content: str
    published_date: strawberry.auto
    directive: strawberry.ID
    type: strawberry.auto
    file: Upload
    cover_image: Upload | None = strawberry.UNSET


@strawberry_django.input(Resource)
class ResourceUpdateInput:
    title: strawberry.auto
    content: str
    published_date: strawberry.auto
    directive: strawberry.ID
    type: strawberry.auto
    file: Upload | None = strawberry.UNSET
    cover_image: Upload | None = strawberry.UNSET


@strawberry_django.input(Resource)
class ResourceDeleteInput:
    id: strawberry.ID
