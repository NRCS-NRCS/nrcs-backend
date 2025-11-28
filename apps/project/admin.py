from django.contrib import admin

from apps.common.admin import UserResourceAdmin

# Register your models here.
from apps.project.models import Project


@admin.register(Project)
class ProjectAdmin(UserResourceAdmin):
    list_display = ("title",)
    search_fields = ("title",)
    list_select_related = True
