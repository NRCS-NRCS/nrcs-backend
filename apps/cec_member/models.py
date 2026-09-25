from django.db import models
from django.utils.translation import gettext_lazy as _
from django_choices_field import IntegerChoicesField

from apps.common.models import UserResource
from utils.common import MAX_IMAGE_FILE_SIZE, validate_file_size


class CecMemberTypeEnum(models.IntegerChoices):
    OFFICE_BEARER = 1, "Office Bearer"
    MEMBER = 2, "Member"
    STAFF = 3, "Staff"


class CecMember(UserResource):
    """A member of the Central Executive Committee (or its supporting staff)."""

    name = models.CharField(_("Name"), max_length=255)
    member_type = IntegerChoicesField(choices_enum=CecMemberTypeEnum, default=CecMemberTypeEnum.MEMBER)
    designation = models.CharField(
        _("Designation"),
        max_length=255,
        null=True,
        blank=True,
        help_text=_("Shown as the heading for office bearers and staff, e.g. Chairperson."),
    )
    email = models.EmailField(_("Email"), null=True, blank=True)
    secondary_email = models.EmailField(_("Secondary email"), null=True, blank=True)
    address = models.CharField(_("Address"), max_length=255, null=True, blank=True)
    contact_number = models.CharField(_("Contact number"), max_length=50, null=True, blank=True)
    photo = models.ImageField(_("Photo"), upload_to="cec-member/", blank=True, null=True)
    order_index = models.IntegerField(_("Order index"), default=0)
    is_active = models.BooleanField(
        _("Is active"),
        default=True,
        help_text=_("Inactive members are kept in the CMS but hidden from the website."),
    )

    def clean(self):
        if self.photo:
            validate_file_size(self.photo, MAX_IMAGE_FILE_SIZE)
        return super().clean()

    def __str__(self):
        return self.name

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        db_table = "cec_member"
        verbose_name = _("CEC member")
        verbose_name_plural = _("CEC members")
        ordering = ["order_index", "id"]
