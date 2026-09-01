import httpx
import strawberry
import strawberry_django
from strawberry_django.permissions import IsSuperuser

from apps.common import github
from main.graphql.context import Info
from utils.graphql.drf import MutationCustomErrorType
from utils.graphql.types import MutationResponseType

from .types import DeploymentTriggerType


@strawberry.type
class Mutation:
    @strawberry_django.mutation(extensions=[IsSuperuser()])
    async def trigger_deployment(self, info: Info) -> MutationResponseType[DeploymentTriggerType]:
        """Dispatch the public site's deployment workflow.

        Takes no ref: the branch comes from settings.GITHUB_DEFAULT_REF so a CMS user
        can never point a production deploy at an arbitrary branch.
        """
        try:
            runs = await github.afetch_runs()
        except httpx.HTTPError as e:
            raise github.describe_http_error(e, "check for running deployments") from e

        if github.has_active_run(runs):
            return MutationResponseType(
                ok=False,
                errors=MutationCustomErrorType.generate_message("A deployment is already running."),
            )

        try:
            ref = await github.atrigger_dispatch()
        except (github.DeploymentError, httpx.HTTPError) as e:
            return MutationResponseType(
                ok=False,
                errors=MutationCustomErrorType.generate_message(f"Failed to trigger deployment: {e}"),
            )

        # NOTE: GitHub answers a dispatch with 204 and no body, so there is no run to return
        # here and the new run takes a few seconds to appear in the runs list. The client
        # shows an optimistic "deploying" state and polls until it shows up.
        return MutationResponseType(
            ok=True,
            result=DeploymentTriggerType(ref=ref, workflow_url=github.workflow_url()),
        )
