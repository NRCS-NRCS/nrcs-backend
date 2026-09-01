import datetime

import strawberry

from apps.common import github
from apps.users.graphql.types import UserMeType, UserResourceTypeMixin, UserType

DeploymentStatusEnum = strawberry.enum(github.DeploymentStatusEnum)


def _parse_datetime(value: str | None) -> datetime.datetime | None:
    if not value:
        return None
    return datetime.datetime.fromisoformat(value)


@strawberry.type
class DeploymentType:
    """A single GitHub Actions run of the public site's deployment workflow."""

    id: strawberry.ID
    run_number: int
    title: str
    branch: str
    # How the run started: "workflow_dispatch" for CMS/manual triggers, "push" for automatic ones.
    event: str
    status: DeploymentStatusEnum  # type: ignore[reportInvalidTypeForm]
    url: str
    actor: str | None
    created_at: datetime.datetime | None
    started_at: datetime.datetime | None
    updated_at: datetime.datetime | None

    @classmethod
    def from_run(cls, run: dict) -> "DeploymentType":
        # NOTE: For workflow_dispatch runs the actor is whoever owns GITHUB_TOKEN, not the
        # CMS user who pressed the button. Attributing to a CMS user needs a stored model.
        actor = run.get("triggering_actor") or run.get("actor") or {}
        return cls(
            id=strawberry.ID(str(run["id"])),
            run_number=run.get("run_number") or 0,
            title=run.get("display_title") or run.get("name") or "",
            branch=run.get("head_branch") or "",
            event=run.get("event") or "",
            status=github.derive_status(run),
            url=run.get("html_url") or github.workflow_url(),
            actor=actor.get("login"),
            created_at=_parse_datetime(run.get("created_at")),
            started_at=_parse_datetime(run.get("run_started_at")),
            updated_at=_parse_datetime(run.get("updated_at")),
        )


@strawberry.type
class DeploymentListType:
    results: list[DeploymentType]
    # Server-derived so the client doesn't re-implement the guard. Drives both the
    # disabled state of the trigger button and whether the frontend polls.
    has_active_run: bool
    workflow_url: str


@strawberry.type
class DeploymentTriggerType:
    ref: str
    workflow_url: str


__all__ = [
    "DeploymentListType",
    "DeploymentStatusEnum",
    "DeploymentTriggerType",
    "DeploymentType",
    "UserMeType",
    "UserResourceTypeMixin",
    "UserType",
]
