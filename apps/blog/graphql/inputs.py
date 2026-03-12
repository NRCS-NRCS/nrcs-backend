import strawberry
import strawberry_django
from strawberry.file_uploads import Upload

from apps.blog.models import Blog


# NOTE: Make sure this matches with the serializers ../serializers.py
@strawberry_django.input(Blog)
class BlogCreateInput:
    title: strawberry.auto
    published_date: strawberry.auto
    author: strawberry.auto
    content: str
    featured: strawberry.auto
    status: strawberry.auto
    cover_image: Upload | None = strawberry.UNSET
    department: strawberry.ID | None = strawberry.UNSET
    directive: strawberry.ID | None = strawberry.UNSET


@strawberry_django.partial(Blog)
class BlogUpdateInput:
    title: strawberry.auto
    published_date: strawberry.auto
    author: strawberry.auto
    content: str
    featured: strawberry.auto
    status: strawberry.auto
    cover_image: Upload | None = strawberry.UNSET
    department: strawberry.ID | None = strawberry.UNSET
    directive: strawberry.ID | None = strawberry.UNSET


@strawberry_django.input(Blog)
class BlogDeleteInput:
    id: strawberry.ID
