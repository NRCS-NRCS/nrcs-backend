from django.contrib import admin

from apps.common.admin import UserResourceAdmin

from .models import JobVacancy


@admin.register(JobVacancy)
class JobVacancyAdmin(UserResourceAdmin):
    list_display = ("position", "expiry_date", "number_of_vacancies")
    list_filter = ("expiry_date",)
    list_select_related = ("department",)
