from django.db import models
from mdeditor.fields import MDTextField

from apps.common.models import UserResource
from utils.common import MAX_HIGHLIGHT_FILE_SIZE, MAX_IMAGE_FILE_SIZE, validate_file_size
from utils.embed import validate_embeds


# Create your models here.
class Highlight(UserResource):
    heading = models.CharField(max_length=255)
    description = MDTextField()
    image = models.FileField(upload_to="highlights/")
    is_active = models.BooleanField(default=False)
    show_in_popup = models.BooleanField(default=False)

    def __str__(self):
        return self.heading

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Only one highlight may be shown in the popup at a time; enabling it here
        # clears the flag on every other highlight.
        if self.show_in_popup:
            Highlight.objects.exclude(pk=self.pk).filter(show_in_popup=True).update(show_in_popup=False)

    def clean(self):
        if self.image:
            validate_file_size(self.image, MAX_IMAGE_FILE_SIZE)
        validate_embeds(self.description)
        return super().clean()


class ActionLink(models.Model):
    url = models.URLField()
    label = models.CharField(max_length=255)
    highlight = models.ForeignKey(Highlight, on_delete=models.SET_NULL, null=True, blank=True, related_name="action_links")

    def __str__(self):
        return self.label


class HighlightFile(models.Model):
    MAX_FILES_PER_HIGHLIGHT = 50

    file = models.FileField(upload_to="highlights/files/")
    order = models.PositiveIntegerField()
    label = models.CharField(max_length=255, blank=True)
    highlight = models.ForeignKey(Highlight, on_delete=models.SET_NULL, null=True, blank=True, related_name="files")

    class Meta:
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(fields=["highlight", "order"], name="unique_highlight_file_order_per_highlight"),
        ]

    def __str__(self):
        return self.label or f"File {self.order}"

    def clean(self):
        if self.file:
            validate_file_size(self.file, MAX_HIGHLIGHT_FILE_SIZE)
        return super().clean()


class KeyStat(models.Model):
    MAX_FEATURED_PER_HIGHLIGHT = 4

    order = models.PositiveIntegerField()
    title = models.CharField(max_length=255)
    stat = models.IntegerField()
    featured = models.BooleanField(default=False)
    highlight = models.ForeignKey(Highlight, on_delete=models.SET_NULL, null=True, blank=True, related_name="key_stats")

    class Meta:
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(fields=["highlight", "order"], name="unique_key_stat_order_per_highlight"),
        ]

    def __str__(self):
        return self.title
