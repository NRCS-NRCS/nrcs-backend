from django.contrib import admin

from apps.common.admin import UserResourceAdmin

# Register your models here.
from apps.project.models import Project


@admin.register(Project)
class ProjectAdmin(UserResourceAdmin):
    list_display = ("title", "strategic_directive", "start_date", "end_date")
    search_fields = ("title", "strategic_directive__title")
    list_filter = ["strategic_directive"]
    list_select_related = True
