from django.db import models

from apps.common.models import UserResource


class PartnerScope(models.TextChoices):
    LOCAL = "local", "Local"
    GLOBAL = "global", "Global"


# make a model
class Partner(UserResource):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to="partner/", blank=True, null=True)
    scope = models.CharField(max_length=255, choices=PartnerScope.choices)

    def __str__(self):
        return self.title

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        db_table = "partner"
        verbose_name = "Partner"
        verbose_name_plural = "Partners"
