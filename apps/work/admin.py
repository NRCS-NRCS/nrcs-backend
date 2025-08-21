from django.contrib import admin

from apps.common.admin import UserResourceAdmin

# Register your models here.
from apps.work.models import Work


@admin.register(Work)
class WorkAdmin(UserResourceAdmin):
    list_display = ("title", "department", "strategic_directive", "start_date", "end_date")
    search_fields = ("title", "department__title", "strategic_directive__title")
    list_filter = ["department", "strategic_directive"]
    list_select_related = True
