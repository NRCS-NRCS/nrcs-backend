from apps.users.tests.factory import UserFactory
from main.tests.base_test import TestCase

_USER_FRAGMENT = """
  id
  email
  firstName
  lastName
  isActive
  userType
"""


class TestUserQuery(TestCase):
    class Query:
        ME = f"""
          query {{
            me {{
              {_USER_FRAGMENT}
            }}
          }}
        """
        USERS = """
          query users($pagination: OffsetPaginationInput) {
            users(pagination: $pagination) {
              results {
                id
                email
                userType
              }
            }
          }
        """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = UserFactory.create(email="query-test-user@example.com", is_staff=True)

    def test_me_authenticated(self):
        self.force_login(self.user)
        content = self.query_check(self.Query.ME)
        me = content["data"]["me"]
        assert me is not None
        assert me["email"] == self.user.email

    def test_me_unauthenticated(self):
        self.logout()
        content = self.query_check(self.Query.ME)
        assert content["data"]["me"] is None
