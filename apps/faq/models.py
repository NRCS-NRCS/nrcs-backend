from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import UserResource


class Faq(UserResource):
    question = models.CharField(_("Question"), max_length=255)
    answer = models.TextField(_("Answer"))
    order_index = models.IntegerField(_("Order Index"), default=0)

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        verbose_name = _("Faq")
        verbose_name_plural = _("Faq")

    def __str__(self):
        return self.question
