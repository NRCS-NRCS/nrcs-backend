from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from apps.common.models import UserResource
from apps.strategic.models import StrategicDirectives
from utils.common import unique_slugify


# Create your models here.
class Department(UserResource):
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    description = models.TextField()
    strategic_directive = models.ForeignKey(
        StrategicDirectives,
        on_delete=models.CASCADE,
        verbose_name=_("Strategic Directive"),
        null=True,
        blank=True,
    )
    contact_person_name = models.CharField(max_length=255, verbose_name=_("Contact Person Name"), null=True, blank=True)
    contact_person_email = models.EmailField(max_length=255, verbose_name=_("Contact Person Email"), null=True, blank=True)
    slug = models.SlugField(unique=True, max_length=250, blank=True, verbose_name=_("Slug"))

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(self, slugify(self.title))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        verbose_name = _("Department")
        verbose_name_plural = _("Departments")
