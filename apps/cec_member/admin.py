from django.contrib import admin

from apps.cec_member.models import CecMember
from apps.common.admin import UserResourceAdmin


@admin.register(CecMember)
class CecMemberAdmin(UserResourceAdmin):
    list_display = ("name", "member_type", "designation", "order_index", "is_active")
    list_filter = ("member_type", "is_active")
    search_fields = ("name", "designation", "email")
    ordering = ("order_index", "id")
    readonly_fields = (
        "created_by",
        "modified_by",
    )
