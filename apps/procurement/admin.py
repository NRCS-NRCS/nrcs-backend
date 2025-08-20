from django.contrib import admin

from .models import Procurement


# Register your models here.
@admin.register(Procurement)
class ProcurementAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "published_date", "expiry_date")
    search_fields = ("title", "description", "published_date", "expiry_date")
