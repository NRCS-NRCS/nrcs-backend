from django.contrib import admin

from apps.common.admin import UserResourceAdmin
from apps.partner.models import Partner


@admin.register(Partner)
class PartnerAdmin(UserResourceAdmin):
    list_display = ("title", "scope", "image")
    list_filter = ("scope",)
    search_fields = ("title",)
    ordering = ("title",)
    readonly_fields = (
        "created_by",
        "modified_by",
    )
