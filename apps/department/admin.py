from django.contrib import admin

from apps.common.admin import UserResourceAdmin
from apps.department.models import Department


# Register your models here.
@admin.register(Department)
class DepartmentAdmin(UserResourceAdmin):
    list_display = ("title", "description", "contact_person_name", "contact_person_email")
    search_fields = ("title", "description", "contact_person_name", "contact_person_email")
    list_filter = ["strategic_directive"]
    list_select_related = True
