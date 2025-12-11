from django.contrib import admin

from .models import ActionLink, Highlight


class ActionLinkInline(admin.TabularInline):  # Tabular inline form
    model = ActionLink
    extra = 1  # show 1 empty row by default


@admin.register(Highlight)
class HighlightAdmin(admin.ModelAdmin):
    list_display = ("heading", "is_active")
    search_fields = ("heading", "description")
    inlines = [ActionLinkInline]


# @admin.register(ActionLink)
# class ActionLinkAdmin(admin.ModelAdmin):
#     list_display = ("label", "url", "highlight")   # tabular view
#     search_fields = ("label", "url")
#     list_filter = ("highlight",)
#     ordering = ("label",)
