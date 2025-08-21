from django.db import models

# from markdownx.models import MarkdownxField
from mdeditor.fields import MDTextField

from apps.common.models import UserResource


class Resource(UserResource):
    title = models.CharField(max_length=255)
    content = MDTextField(blank=True, null=True)
    file = models.FileField(upload_to="resources/", null=True, blank=True)
    published_date = models.DateField()

    def __str__(self):
        return self.title
