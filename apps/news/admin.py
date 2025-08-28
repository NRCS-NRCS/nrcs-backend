from django.contrib import admin

from apps.common.admin import UserResourceAdmin

from .models import News


@admin.register(News)
class NewsAdmin(UserResourceAdmin):
    list_display = ["title", "status"]
