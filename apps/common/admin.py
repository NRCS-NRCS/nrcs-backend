# make a base admin class for auto created by and modified by


import httpx
from django.conf import settings
from django.contrib import admin, messages
from django.template.response import TemplateResponse
from django.urls import path

from apps.common import github


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


# ---- Custom admin page: /admin/deployments/ ----
# NOTE: The CMS has its own deployments view backed by the same apps.common.github
# helpers. This page is kept as a fallback for when the CMS frontend is unavailable.


def deployments_view(request):
    runs = []
    error = None

    try:
        runs = github.fetch_runs()
    except (httpx.HTTPError, github.DeploymentError) as e:
        error = str(e)

    is_workflow_active = github.has_active_run(runs)

    if request.method == "POST":
        action = request.POST.get("action")

        # ---- Guard rails ----
        if action != "trigger":
            messages.error(request, "Unknown action.")
        elif not request.user.is_superuser:
            messages.error(request, "You do not have permission to deploy.")
        elif is_workflow_active:
            messages.warning(request, "A deployment is already running.")
        else:
            try:
                ref = github.trigger_dispatch()
                messages.success(request, f"Deployment triggered on '{ref}'.")
                # refresh state
                runs = github.fetch_runs()
                is_workflow_active = github.has_active_run(runs)
            except (httpx.HTTPError, github.DeploymentError) as e:
                messages.error(request, f"Failed to trigger deployment: {e}")

    context = {
        **admin.site.each_context(request),
        "title": "Deployments",
        "runs": runs,
        "error": error,
        "has_active_run": is_workflow_active,
        "repo_url": github.workflow_url(),
        "default_ref": settings.GITHUB_DEFAULT_REF,
    }
    return TemplateResponse(request, "admin/deployments.html", context)


def inject_deployments_url(original_get_urls):
    def get_urls():
        urls = list(original_get_urls())

        if not settings.GITHUB_TOKEN:
            return urls

        # If already added, don't add again
        if any(getattr(u, "name", None) == "deployments" for u in urls):
            return urls

        return [
            path("deployments/", admin.site.admin_view(deployments_view), name="deployments"),
            *urls,
        ]

    return get_urls


admin.site.get_urls = inject_deployments_url(admin.site.get_urls)
