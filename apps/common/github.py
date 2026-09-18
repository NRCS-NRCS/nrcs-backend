"""GitHub Actions integration used to list and trigger public-site deployments.

The deployment being managed here is the *public website* (``GITHUB_REPO``),
not this CMS. Both the Django admin page (sync) and the GraphQL layer (async)
go through this module so the API contract lives in exactly one place.
"""

import enum

import httpx
from django.conf import settings

GITHUB_API_ROOT = "https://api.github.com"
REQUEST_TIMEOUT = 10
DEFAULT_RUN_LIMIT = 10

# Run statuses that mean "not finished yet".
# https://docs.github.com/en/rest/actions/workflow-runs
ACTIVE_RUN_STATUSES = frozenset({"queued", "in_progress", "waiting", "pending", "requested"})


class DeploymentError(RuntimeError):
    """A deployment could not be listed or triggered."""


class DeploymentStatusEnum(enum.Enum):
    """GitHub's ``status`` and ``conclusion`` collapsed into the one value the UI renders."""

    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    UNKNOWN = "unknown"


_CONCLUSION_MAP: dict[str, DeploymentStatusEnum] = {
    "success": DeploymentStatusEnum.SUCCESS,
    "neutral": DeploymentStatusEnum.SUCCESS,
    "failure": DeploymentStatusEnum.FAILED,
    "timed_out": DeploymentStatusEnum.FAILED,
    "startup_failure": DeploymentStatusEnum.FAILED,
    "action_required": DeploymentStatusEnum.FAILED,
    "cancelled": DeploymentStatusEnum.CANCELLED,
    "skipped": DeploymentStatusEnum.CANCELLED,
    "stale": DeploymentStatusEnum.CANCELLED,
}


def derive_status(run: dict) -> DeploymentStatusEnum:
    """Map a workflow run onto DeploymentStatusEnum.

    Anything GitHub adds later falls through to UNKNOWN rather than raising, so a new
    upstream status value cannot break the whole deployments query.
    """
    status = run.get("status")
    if status == "in_progress":
        return DeploymentStatusEnum.IN_PROGRESS
    if status in ACTIVE_RUN_STATUSES:
        return DeploymentStatusEnum.QUEUED
    if status != "completed":
        return DeploymentStatusEnum.UNKNOWN
    conclusion = run.get("conclusion") or ""
    return _CONCLUSION_MAP.get(str(conclusion), DeploymentStatusEnum.UNKNOWN)


def has_active_run(runs: list[dict]) -> bool:
    return any(run.get("status") in ACTIVE_RUN_STATUSES for run in runs)


def workflow_url() -> str:
    """Human-facing GitHub URL for the deployment workflow."""
    return (
        f"https://github.com/{settings.GITHUB_OWNER}/{settings.GITHUB_REPO}"
        f"/actions/workflows/{settings.GITHUB_WORKFLOW_FILE}"
    )


def _workflow_api_url(action: str) -> str:
    return (
        f"{GITHUB_API_ROOT}/repos/{settings.GITHUB_OWNER}/{settings.GITHUB_REPO}"
        f"/actions/workflows/{settings.GITHUB_WORKFLOW_FILE}/{action}"
    )


def _headers() -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = getattr(settings, "GITHUB_TOKEN", None)
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _parse_runs(response: httpx.Response) -> list[dict]:
    response.raise_for_status()
    return response.json().get("workflow_runs", [])


def _dispatch_payload(ref: str | None) -> dict:
    if not settings.GITHUB_TOKEN:
        raise DeploymentError("GITHUB_TOKEN is not set (needs Actions: read & write to trigger).")
    return {"ref": ref or settings.GITHUB_DEFAULT_REF}


def describe_http_error(error: httpx.HTTPError, action: str) -> DeploymentError:
    """Turn an httpx failure into a message that says what to actually go and fix.

    A 404 here almost always means the GITHUB_* settings point at a workflow that
    isn't there, which is a very different problem from GitHub being unreachable.
    """
    if not isinstance(error, httpx.HTTPStatusError):
        return DeploymentError(f"Could not reach GitHub to {action}.")

    status = error.response.status_code
    target = f"{settings.GITHUB_OWNER}/{settings.GITHUB_REPO}"

    if status == httpx.codes.NOT_FOUND:
        return DeploymentError(
            f"GitHub has no workflow '{settings.GITHUB_WORKFLOW_FILE}' in {target}"
            " (or the token cannot see it). Check GITHUB_OWNER, GITHUB_REPO and"
            " GITHUB_WORKFLOW_FILE.",
        )
    if status in (httpx.codes.UNAUTHORIZED, httpx.codes.FORBIDDEN):
        return DeploymentError(
            f"GitHub rejected the request with {status}. GITHUB_TOKEN is likely missing"
            f" 'Actions: Read and write' on {target}.",
        )
    return DeploymentError(f"GitHub returned {status} while trying to {action}.")


def _check_dispatch(response: httpx.Response) -> None:
    # A successful dispatch is 204 No Content. GitHub returns no run id, so the caller
    # cannot identify the run it just created — it has to poll the runs list for it.
    if response.status_code != httpx.codes.NO_CONTENT:
        raise DeploymentError(f"Dispatch failed: {response.status_code} {response.text}")


# -- Sync (Django admin)


def fetch_runs(limit: int = DEFAULT_RUN_LIMIT) -> list[dict]:
    return _parse_runs(
        httpx.get(
            _workflow_api_url("runs"),
            params={"per_page": limit},
            headers=_headers(),
            timeout=REQUEST_TIMEOUT,
        ),
    )


def trigger_dispatch(ref: str | None = None) -> str:
    payload = _dispatch_payload(ref)
    _check_dispatch(
        httpx.post(
            _workflow_api_url("dispatches"),
            json=payload,
            headers=_headers(),
            timeout=REQUEST_TIMEOUT,
        ),
    )
    return payload["ref"]


# -- Async (GraphQL)


async def afetch_runs(limit: int = DEFAULT_RUN_LIMIT) -> list[dict]:
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        response = await client.get(
            _workflow_api_url("runs"),
            params={"per_page": limit},
            headers=_headers(),
        )
    return _parse_runs(response)


async def atrigger_dispatch(ref: str | None = None) -> str:
    payload = _dispatch_payload(ref)
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        response = await client.post(
            _workflow_api_url("dispatches"),
            json=payload,
            headers=_headers(),
        )
    _check_dispatch(response)
    return payload["ref"]
