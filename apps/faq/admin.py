from django.contrib import admin

from apps.common.admin import UserResourceAdmin

from .models import Faq


@admin.register(Faq)
class FaqAdmin(UserResourceAdmin):
    list_display = ("question", "answer", "order_index")
    search_fields = ("question", "answer")
    list_filter = ["order_index"]
    list_select_related = True
