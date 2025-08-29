from django.contrib import admin

from apps.common.admin import UserResourceAdmin
from apps.radio_program.models import RadioProgram


@admin.register(RadioProgram)
class RadioProgramAdmin(UserResourceAdmin):
    list_display = ("title", "published_date")
