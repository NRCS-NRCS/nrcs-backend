from django.contrib import admin

# Register your models here.
from apps.strategic.models import MajorResponsibilities, StrategicDirectives


@admin.register(StrategicDirectives)
class StrategicDirectivesAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "contact_person_name", "contact_person_email")
    search_fields = ("title", "description", "contact_person_name", "contact_person_email")
    list_filter = ("title", "description", "contact_person_name", "contact_person_email")
    ordering = ("title",)
    prepopulated_fields = {"slug": ("title",)}


@admin.register(MajorResponsibilities)
class MajorResponsibilitiesAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "directive")
    search_fields = ("title", "description", "directive__title")
    list_filter = ("title", "description", "directive")
    ordering = ("title",)
    prepopulated_fields = {"slug": ("title",)}
