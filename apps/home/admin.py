from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet

from .models import ActionLink, Highlight, HighlightFile, KeyStat


class ActionLinkInline(admin.TabularInline):  # Tabular inline form
    model = ActionLink
    extra = 1  # show 1 empty row by default


class HighlightFileInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        file_count = 0
        for form in self.forms:
            # Skip forms without cleaned_data (empty extra rows) or marked for deletion.
            if not getattr(form, "cleaned_data", None) or form.cleaned_data.get("DELETE"):
                continue
            if form.cleaned_data.get("file"):
                file_count += 1
        if file_count > HighlightFile.MAX_FILES_PER_HIGHLIGHT:
            raise ValidationError(
                f"A highlight can have at most {HighlightFile.MAX_FILES_PER_HIGHLIGHT} files.",
            )


class HighlightFileInline(admin.TabularInline):  # Tabular inline form
    model = HighlightFile
    formset = HighlightFileInlineFormSet
    extra = 1  # show 1 empty row by default


class KeyStatInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        featured_count = 0
        for form in self.forms:
            # Skip forms without cleaned_data (empty extra rows) or marked for deletion.
            if not getattr(form, "cleaned_data", None) or form.cleaned_data.get("DELETE"):
                continue
            if form.cleaned_data.get("featured"):
                featured_count += 1
        if featured_count > KeyStat.MAX_FEATURED_PER_HIGHLIGHT:
            raise ValidationError(
                f"A highlight can have at most {KeyStat.MAX_FEATURED_PER_HIGHLIGHT} featured key stats.",
            )


class KeyStatInline(admin.TabularInline):  # Tabular inline form
    model = KeyStat
    formset = KeyStatInlineFormSet
    extra = 1  # show 1 empty row by default


@admin.register(Highlight)
class HighlightAdmin(admin.ModelAdmin):
    list_display = ("heading", "is_active", "show_in_popup")
    search_fields = ("heading", "description")
    inlines = [ActionLinkInline, KeyStatInline, HighlightFileInline]
