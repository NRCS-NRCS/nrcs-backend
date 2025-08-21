from django.contrib import admin

from .models import Faq


@admin.register(Faq)
class FaqAdmin(admin.ModelAdmin):
    list_display = ("question", "answer", "order_index")
    search_fields = ("question", "answer")
    list_filter = ["order_index"]
    list_select_related = True
