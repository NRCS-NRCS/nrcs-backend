from django.contrib import admin

from apps.common.admin import UserResourceAdmin

# Register your models here.
from apps.strategic.models import MajorResponsibilities, StrategicDirectives


@admin.register(StrategicDirectives)
class StrategicDirectivesAdmin(UserResourceAdmin):
    list_display = ("title", "contact_person_name", "contact_person_email")
    search_fields = ("title", "contact_person_name", "contact_person_email")
    list_filter = ("title", "contact_person_name", "contact_person_email")
    ordering = ("title",)
    readonly_fields = ("slug",)


@admin.register(MajorResponsibilities)
class MajorResponsibilitiesAdmin(UserResourceAdmin):
    list_display = ("title", "directive")
    search_fields = ("title", "directive__title")
    list_filter = ("title", "directive")
    ordering = ("title",)
    list_select_related = True
    readonly_fields = ("slug",)
