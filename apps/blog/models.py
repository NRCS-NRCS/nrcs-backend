from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django_choices_field import IntegerChoicesField
from mdeditor.fields import MDTextField

from apps.common.models import StatusEnum, UserResource
from apps.department.models import Department
from apps.strategic.models import StrategicDirectives
from utils.common import MAX_IMAGE_FILE_SIZE, unique_slugify, validate_file_size


class Blog(UserResource):
    title = models.CharField(max_length=232, verbose_name=_("Title"))
    published_date = models.DateField(verbose_name=_("Published Date"))
    author = models.CharField(max_length=50, verbose_name=_("Author"))
    content = MDTextField(verbose_name=_("Content"))
    cover_image = models.ImageField(
        upload_to="blogs/",
        verbose_name=_("Cover Image"),
        null=True,
        blank=True,
    )
    featured = models.BooleanField(verbose_name=_("Featured"), default=False)
    status: int = IntegerChoicesField(choices_enum=StatusEnum, default=StatusEnum.DRAFT)  # type: ignore[reportAssignmentType]
    slug = models.SlugField(unique=True, max_length=250, blank=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Department"),
    )
    directive = models.ForeignKey(
        StrategicDirectives,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Strategic Directive"),
    )

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
