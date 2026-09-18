from unittest import mock

import httpx

from apps.users.tests.factory import UserFactory
from main.tests.base_test import TestCase

RUN_COMPLETED = {
    "id": 101,
    "run_number": 7,
    "display_title": "Deploy site",
    "name": "CD",
    "head_branch": "main",
    "event": "workflow_dispatch",
    "status": "completed",
    "conclusion": "success",
    "html_url": "https://github.com/NRCS-NRCS/nrcs-client/actions/runs/101",
    "actor": {"login": "nrcs-bot"},
    "triggering_actor": {"login": "nrcs-bot"},
    "created_at": "2026-08-26T10:00:00Z",
    "run_started_at": "2026-08-26T10:00:05Z",
    "updated_at": "2026-08-26T10:04:00Z",
}

RUN_IN_PROGRESS = {
    **RUN_COMPLETED,
    "id": 102,
    "run_number": 8,
    "status": "in_progress",
    "conclusion": None,
}


class TestDeploymentQuery(TestCase):
    QUERY = """
      query deployments {
        deployments {
          hasActiveRun
          workflowUrl
          results {
            id
            runNumber
            title
            branch
            event
            status
            url
            actor
            createdAt
            startedAt
            updatedAt
          }
        }
      }
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = UserFactory.create(email="viewer@example.com")

    def test_requires_authentication(self):
        self.logout()
        self.query_check(self.QUERY, assert_errors=True)

    def test_any_authenticated_user_can_read(self):
        self.force_login(self.user)
        with mock.patch(
            "apps.common.github.afetch_runs",
            new=mock.AsyncMock(return_value=[RUN_COMPLETED]),
        ):
            content = self.query_check(self.QUERY)

        data = content["data"]["deployments"]
        assert data["hasActiveRun"] is False, content
        assert data["workflowUrl"].startswith("https://github.com/"), content
        assert data["results"] == [
            {
                "id": "101",
                "runNumber": 7,
                "title": "Deploy site",
                "branch": "main",
                "event": "workflow_dispatch",
                "status": "SUCCESS",
                "url": "https://github.com/NRCS-NRCS/nrcs-client/actions/runs/101",
                "actor": "nrcs-bot",
                "createdAt": "2026-08-26T10:00:00+00:00",
                "startedAt": "2026-08-26T10:00:05+00:00",
                "updatedAt": "2026-08-26T10:04:00+00:00",
            },
        ], content

    def test_has_active_run_is_server_derived(self):
        self.force_login(self.user)
        with mock.patch(
            "apps.common.github.afetch_runs",
            new=mock.AsyncMock(return_value=[RUN_IN_PROGRESS, RUN_COMPLETED]),
        ):
            content = self.query_check(self.QUERY)

        data = content["data"]["deployments"]
        assert data["hasActiveRun"] is True, content
        assert data["results"][0]["status"] == "IN_PROGRESS", content

    def test_misconfigured_workflow_says_so(self):
        # A 404 means the GITHUB_* settings point at a workflow that isn't there. That is
        # a config problem, and must not be reported as "GitHub is unreachable".
        self.force_login(self.user)
        request = httpx.Request("GET", "https://api.github.com/")
        not_found = httpx.HTTPStatusError(
            "404",
            request=request,
            response=httpx.Response(404, request=request),
        )
        with mock.patch(
            "apps.common.github.afetch_runs",
            new=mock.AsyncMock(side_effect=not_found),
        ):
            content = self.query_check(self.QUERY, assert_errors=True)

        message = content["errors"][0]["message"]
        assert "GITHUB_WORKFLOW_FILE" in message, content
        assert "Could not reach" not in message, content

    def test_forbidden_points_at_the_token(self):
        self.force_login(self.user)
        request = httpx.Request("GET", "https://api.github.com/")
        forbidden = httpx.HTTPStatusError(
            "403",
            request=request,
            response=httpx.Response(403, request=request),
        )
        with mock.patch(
            "apps.common.github.afetch_runs",
            new=mock.AsyncMock(side_effect=forbidden),
        ):
            content = self.query_check(self.QUERY, assert_errors=True)

        assert "GITHUB_TOKEN" in content["errors"][0]["message"], content

    def test_github_unreachable_errors_rather_than_returning_empty(self):
        # An empty list would be indistinguishable from "never deployed", and would also
        # leave hasActiveRun False, re-enabling the trigger button during an outage.
        self.force_login(self.user)
        with mock.patch(
            "apps.common.github.afetch_runs",
            new=mock.AsyncMock(side_effect=httpx.ConnectError("boom")),
        ):
            self.query_check(self.QUERY, assert_errors=True)
