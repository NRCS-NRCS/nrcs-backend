import strawberry
import strawberry_django

from apps.common.graphql.types import UserResourceTypeMixin
from apps.radio_program.models import RadioProgram
from utils.graphql.types import DjangoFileType


@strawberry_django.type(RadioProgram)
class RadioProgramType(UserResourceTypeMixin):
    id: strawberry.ID
    title: strawberry.auto
    audio_file: DjangoFileType
    published_date: strawberry.auto
    type: strawberry.auto
