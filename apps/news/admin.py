from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet

from apps.common.admin import UserResourceAdmin

from .models import ActionLink, KeyStat, News, NewsFile


class ActionLinkInline(admin.TabularInline):  # Tabular inline form
    model = ActionLink
    extra = 1  # show 1 empty row by default


class NewsFileInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        file_count = 0
        for form in self.forms:
            # Skip forms without cleaned_data (empty extra rows) or marked for deletion.
            if not getattr(form, "cleaned_data", None) or form.cleaned_data.get("DELETE"):
                continue
            if form.cleaned_data.get("file"):
                file_count += 1
        if file_count > NewsFile.MAX_FILES_PER_NEWS:
            raise ValidationError(
                f"A news item can have at most {NewsFile.MAX_FILES_PER_NEWS} files.",
            )


class NewsFileInline(admin.TabularInline):  # Tabular inline form
    model = NewsFile
    formset = NewsFileInlineFormSet
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
        if featured_count > KeyStat.MAX_FEATURED_PER_NEWS:
            raise ValidationError(
                f"A news item can have at most {KeyStat.MAX_FEATURED_PER_NEWS} featured key stats.",
            )


class KeyStatInline(admin.TabularInline):  # Tabular inline form
    model = KeyStat
    formset = KeyStatInlineFormSet
    extra = 1  # show 1 empty row by default


@admin.register(News)
class NewsAdmin(UserResourceAdmin):
    list_display = ["title", "status", "is_highlighted", "show_in_popup"]
    search_fields = ("title", "content")
    inlines = [ActionLinkInline, KeyStatInline, NewsFileInline]
