import strawberry
import strawberry_django
from strawberry.file_uploads import Upload

from apps.project.models import Project


# NOTE: Make sure this matches with the serializers ../serializers.py
@strawberry_django.input(Project)
class ProjectCreateInput:
    title: strawberry.auto
    description: strawberry.auto
    cover_image: Upload | None = strawberry.UNSET
    department: strawberry.ID | None = strawberry.UNSET


# NOTE: Make sure this matches with the serializers ../serializers.py
@strawberry_django.partial(Project)
class ProjectUpdateInput:
    title: strawberry.auto
    description: strawberry.auto
    cover_image: Upload | None = strawberry.UNSET
    department: strawberry.ID | None = strawberry.UNSET


@strawberry_django.input(Project)
class ProjectDeleteInput:
    id: strawberry.ID
