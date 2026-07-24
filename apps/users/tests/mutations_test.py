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
          mutation createUser($data: UserCreateInput!) {{
            createUser(data: $data) {{
              {_USER_RESULT_FRAGMENT}
            }}
          }}
        """
        UPDATE_USER = f"""
          mutation updateUser($data: UserUpdateInput!) {{
            updateUser(data: $data) {{
              {_USER_RESULT_FRAGMENT}
            }}
          }}
        """
        DELETE_USER = f"""
        mutation deleteUser($data: UserDeleteInput!) {{
            deleteUser(data: $data) {{
            {_USER_RESULT_FRAGMENT}
            }}
        }}
        """
        RESET_USER_PASSWORD = f"""
          mutation resetUserPassword($data: PasswordResetInput!, $newPassword: String!) {{
            resetUserPassword(data: $data, newPassword: $newPassword) {{
              {_USER_RESULT_FRAGMENT}
            }}
          }}
        """
        UPDATE_MY_PASSWORD = f"""
          mutation updateMyPassword($data: PasswordUpdateInput!) {{
            updateMyPassword(data: $data) {{
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

    def _assert_permission_denied(self, content: dict, mutation_name: str) -> None:
        resp = content["data"][mutation_name]
        assert resp["__typename"] == "OperationInfo", content
        assert any(m["kind"] == "PERMISSION" for m in resp["messages"]), content

    # --- create_user (superuser only) ---

    def test_create_viewer_user(self):
        self.force_login(self.admin)
        data = {
            "username": "new-viewer",
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
            "username": "new-staff",
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
            "username": "new-admin",
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
        data = {
            "username": "new-viewer",
            "email": "x@x.com",
            "firstName": "No",
            "lastName": "Perm",
            "password": "securepassword123",
        }
        content = self.query_check(self.Mutation.CREATE_USER, variables={"data": data})
        self._assert_permission_denied(content, "createUser")

    # --- update_user (superuser only, id in data) ---

    def test_update_user_fields(self):
        target = UserFactory.create(email="field-update@example.com")
        self.force_login(self.admin)
        content = self.query_check(
            self.Mutation.UPDATE_USER,
            variables={"data": {"id": str(target.pk), "firstName": "Updated", "lastName": "Name"}},
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
            variables={"data": {"id": str(target.pk), "userType": "ADMIN"}},
        )
        resp = self._get_mutation_payload(content, "updateUser")
        assert resp["ok"] is True, content
        assert resp["result"]["userType"] == "ADMIN"
        target.refresh_from_db()
        assert target.is_staff is True
        assert target.is_superuser is True

    def test_update_user_requires_superuser(self):
        other = UserFactory.create(email="update-other@example.com")
        self.force_login(self.user)
        content = self.query_check(
            self.Mutation.UPDATE_USER,
            variables={"data": {"id": str(other.pk), "firstName": "Hacked"}},
        )
        self._assert_permission_denied(content, "updateUser")

    # --- delete_user (superuser only, soft delete) ---

    def test_delete_user_admin(self):
        target = UserFactory.create(email="delete-target@example.com")
        self.force_login(self.admin)
        content = self.query_check(self.Mutation.DELETE_USER, variables={"data": {"id": str(target.pk)}})
        resp = self._get_mutation_payload(content, "deleteUser")
        assert resp["ok"] is True, content
        assert User.objects.filter(pk=target.pk).exists() is True
        target.refresh_from_db()
        assert target.is_active is False

    def test_delete_user_requires_superuser(self):
        target = UserFactory.create(email="delete-denied@example.com")
        self.force_login(self.user)
        content = self.query_check(self.Mutation.DELETE_USER, variables={"data": {"id": str(target.pk)}})
        self._assert_permission_denied(content, "deleteUser")
        assert User.objects.filter(pk=target.pk).exists() is True

    # --- reset_user_password (superuser only) ---

    def test_reset_user_password_admin(self):
        target = UserFactory.create(email="reset-target@example.com", password="oldpassword123")
        self.force_login(self.admin)
        content = self.query_check(
            self.Mutation.RESET_USER_PASSWORD,
            variables={"data": {"id": str(target.pk)}, "newPassword": "brandnewpass456"},
        )
        resp = self._get_mutation_payload(content, "resetUserPassword")
        assert resp["ok"] is True, content
        assert resp["result"]["id"] == str(target.pk)
        target.refresh_from_db()
        assert target.check_password("brandnewpass456") is True

    def test_reset_user_password_requires_superuser(self):
        target = UserFactory.create(email="reset-denied@example.com", password="oldpassword123")
        self.force_login(self.user)
        content = self.query_check(
            self.Mutation.RESET_USER_PASSWORD,
            variables={"data": {"id": str(target.pk)}, "newPassword": "brandnewpass456"},
        )
        self._assert_permission_denied(content, "resetUserPassword")
        target.refresh_from_db()
        assert target.check_password("oldpassword123") is True

    # --- update_my_password (authenticated) ---

    def test_update_my_password(self):
        target = UserFactory.create(email="my-pass@example.com", password="currentpass123")
        self.force_login(target)
        content = self.query_check(
            self.Mutation.UPDATE_MY_PASSWORD,
            variables={"data": {"currentPassword": "currentpass123", "newPassword": "updatedpass456"}},
        )
        resp = self._get_mutation_payload(content, "updateMyPassword")
        assert resp["ok"] is True, content
        target.refresh_from_db()
        assert target.check_password("updatedpass456") is True

    def test_update_my_password_wrong_current(self):
        target = UserFactory.create(email="my-pass-wrong@example.com", password="currentpass123")
        self.force_login(target)
        content = self.query_check(
            self.Mutation.UPDATE_MY_PASSWORD,
            variables={"data": {"currentPassword": "wrongpass", "newPassword": "updatedpass456"}},
        )
        resp = self._get_mutation_payload(content, "updateMyPassword")
        assert resp["ok"] is False, content
        assert resp["errors"] is not None
        target.refresh_from_db()
        assert target.check_password("currentpass123") is True

    def test_update_my_password_requires_authentication(self):
        content = self.query_check(
            self.Mutation.UPDATE_MY_PASSWORD,
            variables={"data": {"currentPassword": "currentpass123", "newPassword": "updatedpass456"}},
        )
        self._assert_permission_denied(content, "updateMyPassword")
