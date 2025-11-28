from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import UserResource
from apps.department.models import Department


class Project(UserResource):
    title = models.CharField(max_length=255)
    description = models.TextField()
    cover_image = models.ImageField(upload_to="project/cover_image", null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")
