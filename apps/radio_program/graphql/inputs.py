import strawberry
import strawberry_django
from strawberry.file_uploads import Upload

from apps.radio_program.models import RadioProgram


@strawberry_django.input(RadioProgram)
class RadioProgramCreateInput:
    title: strawberry.auto
    published_date: strawberry.auto
    type: strawberry.auto
    audio_file: Upload


@strawberry_django.partial(RadioProgram)
class RadioProgramUpdateInput:
    title: strawberry.auto
    published_date: strawberry.auto
    type: strawberry.auto
    audio_file: Upload | None = strawberry.UNSET


@strawberry_django.input(RadioProgram)
class RadioProgramDeleteInput:
    id: strawberry.ID
