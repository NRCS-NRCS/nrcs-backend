from django.contrib import admin

from .models import JobVacancy


@admin.register(JobVacancy)
class JobVacancyAdmin(admin.ModelAdmin):
    list_display = ("position", "expiry_date", "number_of_vacancies")
    list_filter = ("expiry_date",)
    list_select_related = ("department",)
