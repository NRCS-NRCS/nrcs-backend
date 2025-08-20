from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import UserResource
from utils.fields import SecureFileField


# Create your models here.
class Procurement(UserResource):
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    description = models.TextField()
    file = SecureFileField(verbose_name=_("Procurement file"), upload_to="procurement/", null=True, blank=True)
    published_date = models.DateField()
    expiry_date = models.DateField()

    def __str__(self):
        return self.title
