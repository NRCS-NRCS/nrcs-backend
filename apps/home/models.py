from django.db import models
from mdeditor.fields import MDTextField

from apps.common.models import UserResource
from utils.common import MAX_IMAGE_FILE_SIZE, validate_file_size
from utils.embed import validate_embeds


# Create your models here.
class Highlight(UserResource):
    heading = models.CharField(max_length=255)
    description = MDTextField()
    image = models.FileField(upload_to="highlights/")
    is_active = models.BooleanField(default=False)

    def clean(self):
        if self.image:
            validate_file_size(self.image, MAX_IMAGE_FILE_SIZE)
        validate_embeds(self.description)
        return super().clean()

    def __str__(self):
        return self.heading


class ActionLink(models.Model):
    url = models.URLField()
    label = models.CharField(max_length=255)
    highlight = models.ForeignKey(Highlight, on_delete=models.SET_NULL, null=True, blank=True, related_name="action_links")

    def __str__(self):
        return self.label
