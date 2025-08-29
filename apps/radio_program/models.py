from django.core.exceptions import ValidationError
from django.db import models

from apps.common.models import UserResource

# update audio file only validation
file_extensions = [".mp3", ".aac", ".wav", ".flac", ".ogg"]


def validate_audio_file(value):
    if not any(value.name.endswith(ext) for ext in file_extensions):
        raise ValidationError("Unsupported Audio format")


# Create your models here.
class RadioProgram(UserResource):
    title = models.CharField(max_length=255)
    audio_file = models.FileField(upload_to="audio/", validators=[validate_audio_file])
    published_date = models.DateField()

    def __str__(self):
        return self.title
