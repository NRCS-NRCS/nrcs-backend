from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import UserResource
from utils.common import MAX_FILE_SIZE, validate_file_size


# Create your models here.
class Procurement(UserResource):
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    description = models.TextField()
    file = models.FileField(verbose_name=_("Procurement file"), upload_to="procurement/", null=True, blank=True)
    published_date = models.DateField()
    expiry_date = models.DateField()

    def clean(self):
        if self.file:
            validate_file_size(self.file, MAX_FILE_SIZE)
        return super().clean()

    def __str__(self):
        return self.title

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        verbose_name = _("Procurement")
        verbose_name_plural = _("Procurements")
