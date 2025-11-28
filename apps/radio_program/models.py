from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_choices_field import IntegerChoicesField

from apps.common.models import UserResource

# update audio file only validation
file_extensions = [".mp3", ".aac", ".wav", ".flac", ".ogg"]


def validate_audio_file(value):
    if not any(value.name.endswith(ext) for ext in file_extensions):
        raise ValidationError("Unsupported Audio format")


class RadioProgramTypeEnum(models.IntegerChoices):
    TUESDAY_PROGRAM = 100, _("Tuesday Program")
    TOGETHER_FOR_HUMANITY = 200, _("Together For Humanity")


class RadioProgram(UserResource):
    title = models.CharField(max_length=255)
    audio_file = models.FileField(upload_to="audio/", validators=[validate_audio_file])
    published_date = models.DateField()
    type: int = IntegerChoicesField(
        choices_enum=RadioProgramTypeEnum,
        default=RadioProgramTypeEnum.TUESDAY_PROGRAM,
    )  # type: ignore[reportAssignmentType]

    def __str__(self):
        return self.title
