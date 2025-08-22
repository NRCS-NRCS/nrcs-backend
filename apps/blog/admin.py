from django.contrib import admin

from apps.blog.models import Blog
from apps.common.admin import UserResourceAdmin


@admin.register(Blog)
class BlogAdmin(UserResourceAdmin):
    list_display = ("title", "published_date", "status")
    list_filter = ("status",)
    search_fields = ("title",)
