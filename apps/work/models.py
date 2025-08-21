from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import UserResource
from apps.department.models import Department
from apps.strategic.models import StrategicDirectives


class Work(UserResource):
    title = models.CharField(max_length=255)
    description = models.TextField()
    cover_image = models.ImageField(upload_to="work/", null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    strategic_directive = models.ForeignKey(StrategicDirectives, on_delete=models.SET_NULL, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        verbose_name = _("Work")
        verbose_name_plural = _("Works")
