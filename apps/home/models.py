from django.db import models

from apps.common.models import UserResource
from utils.common import MAX_IMAGE_FILE_SIZE, validate_file_size


# Create your models here.
class Highlight(UserResource):
    heading = models.CharField(max_length=255)
    description = models.TextField()
    image = models.FileField(upload_to="highlights/")
    is_active = models.BooleanField(default=False)

    def clean(self):
        if self.image:
            validate_file_size(self.image, MAX_IMAGE_FILE_SIZE)
        return super().clean()

    def __str__(self):
        return self.heading


class ActionLink(models.Model):
    url = models.URLField()
    label = models.CharField(max_length=255)
    highlight = models.ForeignKey(Highlight, on_delete=models.SET_NULL, null=True, blank=True, related_name="action_links")

    def __str__(self):
        return self.label
