# make a base admin class for auto created by and modified by


import requests
from django.conf import settings
from django.contrib import admin, messages
from django.template.response import TemplateResponse
from django.urls import path


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
OWNER = getattr(settings, "GITHUB_OWNER", "NRCS-NRCS")
REPO = getattr(settings, "GITHUB_REPO", "nrcs-client")
WORKFLOW_FILE = getattr(settings, "GITHUB_WORKFLOW_FILE", "cd.yml")


def _github_headers():
    token = getattr(settings, "GITHUB_TOKEN", None)
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def fetch_latest_workflow_runs(limit=5):
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/workflows/{WORKFLOW_FILE}/runs"
    r = requests.get(
        url,
        params={"per_page": limit},
        headers=_github_headers(),
        timeout=15,
    )
    r.raise_for_status()

    return r.json().get("workflow_runs", [])


def has_active_run(runs):
    # GitHub workflow run status values include: queued, in_progress, completed
    return any((r.get("status") in ("queued", "in_progress")) for r in runs)


def trigger_workflow_dispatch(ref="main", inputs=None):
    token = getattr(settings, "GITHUB_TOKEN", None)
    if not token:
        raise RuntimeError("GITHUB_TOKEN is not set (needs Actions: read & write to trigger).")

    url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/workflows/{WORKFLOW_FILE}/dispatches"
    payload = {"ref": ref}
    if inputs:
        payload["inputs"] = inputs

    r = requests.post(url, json=payload, headers=_github_headers(), timeout=15)

    # success is 204 No Content
    if r.status_code != 204:
        raise RuntimeError(f"Dispatch failed: {r.status_code} {r.text}")


def deployments_view(request):
    runs = []
    error = None

    try:
        runs = fetch_latest_workflow_runs(limit=5)
    except Exception as e:
        error = str(e)

    active = has_active_run(runs)

    if request.method == "POST":
        action = request.POST.get("action")

        # ---- Guard rails ----
        if action != "trigger":
            messages.error(request, "Unknown action.")
        elif not request.user.is_superuser:
            messages.error(request, "You do not have permission to deploy.")
        elif active:
            messages.warning(request, "A deployment is already running.")
        else:
            try:
                ref = request.POST.get("ref") or "main"
                trigger_workflow_dispatch(ref=ref)
                messages.success(request, f"Deployment triggered on '{ref}'.")
                # refresh state
                runs = fetch_latest_workflow_runs(limit=5)
                active = has_active_run(runs)
            except Exception as e:
                messages.error(request, f"Failed to trigger deployment: {e}")

    context = {
        **admin.site.each_context(request),
        "title": "Deployments",
        "runs": runs,
        "error": error,
        "has_active_run": active,
        "repo_url": f"https://github.com/{OWNER}/{REPO}/actions/workflows/{WORKFLOW_FILE}",
        "default_ref": "main",
    }
    return TemplateResponse(request, "admin/deployments.html", context)


def inject_deployments_url(original_get_urls):
    def get_urls():
        urls = list(original_get_urls())

        # If already added, don’t add again
        if any(getattr(u, "name", None) == "deployments" for u in urls):
            return urls

        return [
            path("deployments/", admin.site.admin_view(deployments_view), name="deployments"),
            *urls,
        ]

    return get_urls


admin.site.get_urls = inject_deployments_url(admin.site.get_urls)
