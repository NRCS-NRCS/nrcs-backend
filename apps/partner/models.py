from django.db import models
from django_choices_field import IntegerChoicesField

from apps.common.models import UserResource
from utils.common import MAX_IMAGE_FILE_SIZE, validate_file_size


class PartnerScopeEnum(models.IntegerChoices):
    LOCAL = 1, "Local"
    GLOBAL = 2, "Global"


# make a model
class Partner(UserResource):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to="partner/", blank=True, null=True)
    scope = IntegerChoicesField(choices_enum=PartnerScopeEnum)

    def clean(self):
        if self.image:
            validate_file_size(self.image, MAX_IMAGE_FILE_SIZE)
        return super().clean()

    def __str__(self):
        return self.title

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        db_table = "partner"
        verbose_name = "Partner"
        verbose_name_plural = "Partners"
