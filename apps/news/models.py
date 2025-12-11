from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django_choices_field import IntegerChoicesField
from mdeditor.fields import MDTextField

from apps.common.models import StatusEnum, UserResource
from apps.strategic.models import StrategicDirectives
from utils.common import (
    MAX_FILE_SIZE,
    MAX_IMAGE_FILE_SIZE,
    unique_slugify,
    validate_file_size,
)


# Create your models here.
class News(UserResource):
    title = models.CharField(max_length=255)
    content = MDTextField(blank=True, null=True)
    file = models.FileField(upload_to="news/", null=True, blank=True)
    published_date = models.DateField()
    directive = models.ForeignKey(
        StrategicDirectives,
        on_delete=models.CASCADE,
        related_name="news",
        null=True,
        blank=True,
    )
    slug = models.SlugField(unique=True, max_length=250, blank=True, verbose_name=_("Slug"))
    cover_image = models.ImageField(upload_to="news/", null=True, blank=True)
    status = IntegerChoicesField(choices_enum=StatusEnum, default=StatusEnum.DRAFT)

    def clean(self):
        if self.cover_image:
            validate_file_size(self.cover_image, MAX_IMAGE_FILE_SIZE)
        if self.file:
            validate_file_size(self.file, MAX_FILE_SIZE)
        return super().clean()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(self, slugify(self.title))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        verbose_name = _("News")
        verbose_name_plural = _("News")
