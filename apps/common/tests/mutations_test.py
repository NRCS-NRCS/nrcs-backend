# User mutation tests have been moved to apps/user/tests/mutations_test.py

from unittest import mock

from django.test import override_settings

from apps.users.tests.factory import UserFactory
from main.tests.base_test import TestCase

from .queries_test import RUN_COMPLETED, RUN_IN_PROGRESS


@override_settings(GITHUB_TOKEN="dummy-token", GITHUB_DEFAULT_REF="main")
class TestTriggerDeploymentMutation(TestCase):
    MUTATION = """
      mutation triggerDeployment {
        triggerDeployment {
          ... on OperationInfo {
            __typename
            messages { code field kind message }
          }
          ... on DeploymentTriggerTypeMutationResponseType {
            ok
            errors
            result { ref workflowUrl }
          }
        }
      }
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.viewer = UserFactory.create(email="viewer@example.com")
        cls.staff = UserFactory.create(email="staff@example.com", is_staff=True)
        cls.admin = UserFactory.create(email="admin@example.com", is_staff=True, is_superuser=True)

    def _trigger(self, runs):
        fetch = mock.AsyncMock(return_value=runs)
        dispatch = mock.AsyncMock(return_value="main")
        with (
            mock.patch("apps.common.github.afetch_runs", new=fetch),
            mock.patch("apps.common.github.atrigger_dispatch", new=dispatch),
        ):
            content = self.query_check(self.MUTATION)
        return content, dispatch

    def _assert_permission_denied(self, content):
        resp = content["data"]["triggerDeployment"]
        assert resp["__typename"] == "OperationInfo", content
        assert any(m["kind"] == "PERMISSION" for m in resp["messages"]), content

    def test_anonymous_cannot_trigger(self):
        self.logout()
        content, dispatch = self._trigger([RUN_COMPLETED])
        self._assert_permission_denied(content)
        dispatch.assert_not_awaited()

    def test_viewer_cannot_trigger(self):
        self.force_login(self.viewer)
        content, dispatch = self._trigger([RUN_COMPLETED])
        self._assert_permission_denied(content)
        dispatch.assert_not_awaited()

    def test_staff_cannot_trigger(self):
        # Staff can edit content but deploying stays admin-only.
        self.force_login(self.staff)
        content, dispatch = self._trigger([RUN_COMPLETED])
        self._assert_permission_denied(content)
        dispatch.assert_not_awaited()

    def test_admin_triggers_deployment(self):
        self.force_login(self.admin)
        content, dispatch = self._trigger([RUN_COMPLETED])

        resp = content["data"]["triggerDeployment"]
        assert resp["ok"] is True, content
        assert resp["errors"] is None, content
        assert resp["result"]["ref"] == "main", content
        dispatch.assert_awaited_once()

    def test_ref_is_not_client_controllable(self):
        # The mutation takes no arguments at all, so a caller cannot aim a production
        # deploy at an arbitrary branch.
        assert "$ref" not in self.MUTATION
        self.force_login(self.admin)
        _, dispatch = self._trigger([RUN_COMPLETED])
        dispatch.assert_awaited_once_with()

    def test_rejected_while_a_run_is_active(self):
        self.force_login(self.admin)
        content, dispatch = self._trigger([RUN_IN_PROGRESS])

        resp = content["data"]["triggerDeployment"]
        assert resp["ok"] is False, content
        assert resp["result"] is None, content
        assert "already running" in str(resp["errors"]), content
        dispatch.assert_not_awaited()
