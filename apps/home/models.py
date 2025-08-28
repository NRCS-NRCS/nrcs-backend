from django.db import models

from apps.common.models import UserResource


# Create your models here.
class Highlight(UserResource):
    heading = models.CharField(max_length=255)
    description = models.TextField()
    image = models.FileField(upload_to="highlights/")
    expiry_date = models.DateField()


class ActionLink(models.Model):
    url = models.URLField()
    label = models.CharField(max_length=255)
    highlight = models.ForeignKey(Highlight, on_delete=models.SET_NULL, null=True, blank=True, related_name="action_links")

    def __str__(self):
        return self.label
