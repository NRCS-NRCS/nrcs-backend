# make a base admin class for auto created by and modified by

from django.contrib import admin


class UserResourceAdmin(admin.ModelAdmin):
    readonly_fields = (
        "created_by",
        "modified_by",
    )

    def save_model(self, request, obj, form, change):
        """Automatically set created_by and modified_by in admin."""
        if not obj.pk:  # new object
            obj.created_by = request.user
        obj.modified_by = request.user
        super().save_model(request, obj, form, change)
