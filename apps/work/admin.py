from django.contrib import admin

# Register your models here.
from apps.work.models import Work


@admin.register(Work)
class WorkAdmin(admin.ModelAdmin):
    list_display = ("title", "department", "strategic_directive", "start_date", "end_date")
    search_fields = ("title", "department__title", "strategic_directive__title")
    list_filter = ["department", "strategic_directive"]
    # autocomplete_fields = ("department", "strategic_directive")
    list_select_related = True
