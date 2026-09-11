import httpx
import strawberry
from strawberry_django.permissions import IsAuthenticated

from apps.common import github
from main.graphql.context import Info

from .types import DeploymentListType, DeploymentType


@strawberry.type
class Query:
    @strawberry.field(extensions=[IsAuthenticated()])
    async def deployments(self, info: Info) -> DeploymentListType:
        """Latest runs of the public site's deployment workflow, read live from GitHub.

        Nothing is stored locally, so an unreachable GitHub surfaces as a GraphQL error
        rather than an empty list — an empty list would be indistinguishable from
        "this site has never been deployed".
        """
        try:
            runs = await github.afetch_runs()
        except httpx.HTTPError as e:
            raise github.describe_http_error(e, "list deployments") from e

        return DeploymentListType(
            results=[DeploymentType.from_run(run) for run in runs],
            has_active_run=github.has_active_run(runs),
            workflow_url=github.workflow_url(),
        )
