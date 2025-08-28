from django.contrib import admin

from .models import ActionLink, Highlight


class ActionLinkInline(admin.TabularInline):  # Tabular inline form
    model = ActionLink
    extra = 1  # show 1 empty row by default


@admin.register(Highlight)
class HighlightAdmin(admin.ModelAdmin):
    list_display = ("heading", "expiry_date", "is_active")
    search_fields = ("heading", "description")
    list_filter = ("expiry_date",)
    ordering = ("-expiry_date",)
    inlines = [ActionLinkInline]

    def is_active(self, obj):
        from django.utils import timezone

        if obj.expiry_date >= timezone.now().date():
            return "Expired"
        return "Active"


# @admin.register(ActionLink)
# class ActionLinkAdmin(admin.ModelAdmin):
#     list_display = ("label", "url", "highlight")   # tabular view
#     search_fields = ("label", "url")
#     list_filter = ("highlight",)
#     ordering = ("label",)
