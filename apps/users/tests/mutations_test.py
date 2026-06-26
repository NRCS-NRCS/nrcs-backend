from django.contrib.auth.models import User

from apps.users.tests.factory import UserFactory
from main.tests.base_test import TestCase

_USER_RESULT_FRAGMENT = """
  ... on OperationInfo {
    __typename
    messages { code field kind message }
  }
  ... on UserTypeMutationResponseType {
    ok
    errors
    result {
      id
      email
      firstName
      lastName
      isActive
      userType
    }
  }
"""


class TestUserMutation(TestCase):
    class Mutation:
        CREATE_USER = f"""
          mutation createUser($data: CreateUserInput!) {{
            createUser(data: $data) {{
              {_USER_RESULT_FRAGMENT}
            }}
          }}
        """
        UPDATE_USER = f"""
          mutation updateUser($pk: ID!, $data: UpdateUserInput!) {{
            updateUser(pk: $pk, data: $data) {{
              {_USER_RESULT_FRAGMENT}
            }}
          }}
        """
        DELETE_USER = f"""
          mutation deleteUser($pk: ID!) {{
            deleteUser(pk: $pk) {{
              {_USER_RESULT_FRAGMENT}
            }}
          }}
        """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = UserFactory.create(email="test@example.com")
        cls.admin = UserFactory.create(email="admin@example.com", is_staff=True, is_superuser=True)

    def _get_mutation_payload(self, content: dict, mutation_name: str) -> dict:
        resp = content["data"][mutation_name]
        assert resp.get("__typename") != "OperationInfo", content
        return resp

    # --- create_user ---

    def test_create_viewer_user(self):
        self.force_login(self.admin)
        data = {
            "email": "new-viewer@example.com",
            "firstName": "Viewer",
            "lastName": "User",
            "password": "securepassword123",
        }
        content = self.query_check(self.Mutation.CREATE_USER, variables={"data": data})
        resp = self._get_mutation_payload(content, "createUser")
        assert resp["ok"] is True, content
        assert resp["result"]["userType"] == "VIEWER"

    def test_create_staff_user(self):
        self.force_login(self.admin)
        data = {
            "email": "new-staff@example.com",
            "firstName": "Staff",
            "lastName": "User",
            "password": "securepassword123",
            "userType": "STAFF",
        }
        content = self.query_check(self.Mutation.CREATE_USER, variables={"data": data})
        resp = self._get_mutation_payload(content, "createUser")
        assert resp["ok"] is True, content
        assert resp["result"]["userType"] == "STAFF"
        created = User.objects.get(email="new-staff@example.com")
        assert created.is_staff is True
        assert created.is_superuser is False

    def test_create_admin_user(self):
        self.force_login(self.admin)
        data = {
            "email": "new-admin@example.com",
            "firstName": "Admin",
            "lastName": "User",
            "password": "securepassword123",
            "userType": "ADMIN",
        }
        content = self.query_check(self.Mutation.CREATE_USER, variables={"data": data})
        resp = self._get_mutation_payload(content, "createUser")
        assert resp["ok"] is True, content
        assert resp["result"]["userType"] == "ADMIN"
        created = User.objects.get(email="new-admin@example.com")
        assert created.is_staff is True
        assert created.is_superuser is True

    def test_create_user_requires_superuser(self):
        self.force_login(self.user)
        content = self.query_check(
            self.Mutation.CREATE_USER,
            variables={"data": {"email": "x@x.com", "password": "pass"}},
        )
        resp = content["data"]["createUser"]
        assert resp["__typename"] == "OperationInfo", content
        assert any(m["kind"] == "PERMISSION" for m in resp["messages"]), content

    def test_create_user_duplicate_email(self):
        self.force_login(self.admin)
        data = {"email": self.user.email, "password": "pass123"}
        content = self.query_check(self.Mutation.CREATE_USER, variables={"data": data})
        resp = self._get_mutation_payload(content, "createUser")
        assert resp["ok"] is False, content
        assert resp["errors"] is not None

    # --- update_user ---

    def test_update_user_self(self):
        target = UserFactory.create(email="self-update@example.com")
        self.force_login(target)
        content = self.query_check(
            self.Mutation.UPDATE_USER,
            variables={"pk": str(target.pk), "data": {"firstName": "Updated", "lastName": "Name"}},
        )
        resp = self._get_mutation_payload(content, "updateUser")
        assert resp["ok"] is True, content
        assert resp["result"]["firstName"] == "Updated"
        assert resp["result"]["lastName"] == "Name"

    def test_update_user_type(self):
        target = UserFactory.create(email="type-update@example.com")
        self.force_login(self.admin)
        content = self.query_check(
            self.Mutation.UPDATE_USER,
            variables={"pk": str(target.pk), "data": {"userType": "ADMIN"}},
        )
        resp = self._get_mutation_payload(content, "updateUser")
        assert resp["ok"] is True, content
        assert resp["result"]["userType"] == "ADMIN"
        target.refresh_from_db()
        assert target.is_staff is True
        assert target.is_superuser is True

    def test_update_user_admin_can_update_any(self):
        target = UserFactory.create(email="update-target@example.com")
        self.force_login(self.admin)
        content = self.query_check(
            self.Mutation.UPDATE_USER,
            variables={"pk": str(target.pk), "data": {"firstName": "AdminUpdated"}},
        )
        resp = self._get_mutation_payload(content, "updateUser")
        assert resp["ok"] is True, content
        assert resp["result"]["firstName"] == "AdminUpdated"

    def test_update_user_permission_denied(self):
        other = UserFactory.create(email="update-other@example.com")
        self.force_login(self.user)
        content = self.query_check(
            self.Mutation.UPDATE_USER,
            variables={"pk": str(other.pk), "data": {"firstName": "Hacked"}},
        )
        resp = self._get_mutation_payload(content, "updateUser")
        assert resp["ok"] is False, content
        assert resp["errors"] is not None

    # --- delete_user ---

    def test_delete_user_admin(self):
        target = UserFactory.create(email="delete-target@example.com")
        self.force_login(self.admin)
        content = self.query_check(self.Mutation.DELETE_USER, variables={"pk": str(target.pk)})
        resp = self._get_mutation_payload(content, "deleteUser")
        assert resp["ok"] is True, content
        assert resp["result"]["isActive"] is False
        target.refresh_from_db()
        assert target.is_active is False

    def test_delete_user_permission_denied(self):
        target = UserFactory.create(email="delete-denied@example.com")
        self.force_login(self.user)
        content = self.query_check(self.Mutation.DELETE_USER, variables={"pk": str(target.pk)})
        resp = self._get_mutation_payload(content, "deleteUser")
        assert resp["ok"] is False, content
        assert resp["errors"] is not None
        target.refresh_from_db()
        assert target.is_active is True
