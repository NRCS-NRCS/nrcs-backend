from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from apps.common.models import UserResource
from utils.common import MAX_IMAGE_FILE_SIZE, unique_slugify, validate_file_size


class StrategicDirectives(UserResource):
    title = models.CharField(max_length=255, verbose_name=_("Strategic Directive Title"))
    description = models.TextField(verbose_name=_("Strategic Directive Description"))
    cover_image = models.ImageField(
        upload_to="strategic_directives/cover_images",
        verbose_name=_("Cover Image"),
        null=True,
        blank=True,
    )
    slug = models.SlugField(unique=True, max_length=250, blank=True, verbose_name=_("Slug"))

    def clean(self):
        if self.cover_image:
            validate_file_size(self.cover_image, MAX_IMAGE_FILE_SIZE)
        return super().clean()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(self, slugify(self.title))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        verbose_name = _("Strategic Directive")
        verbose_name_plural = _("Strategic Directives")


class MajorResponsibilities(UserResource):
    title = models.CharField(max_length=255, verbose_name=_("Major Responsibility Title"))
    description = models.TextField(verbose_name=_("Major Responsibility Description"))
    directive = models.ForeignKey(
        StrategicDirectives,
        on_delete=models.CASCADE,
        verbose_name=_("Strategic Directive"),
        related_name="major_responsibilities",
    )
    slug = models.SlugField(unique=True, max_length=250, blank=True, verbose_name=_("Slug"))

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(self, slugify(self.title))
        super().save(*args, **kwargs)

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        verbose_name = _("Major Responsibility")
        verbose_name_plural = _("Major Responsibilities")
