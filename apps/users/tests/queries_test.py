from apps.users.tests.factory import UserFactory
from main.tests.base_test import TestCase

_USER_FRAGMENT = """
  id
  email
  fullName
  role
  isActive
  isStaff
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
              count
              results {
                id
                email
                role
              }
            }
          }
        """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = UserFactory.create(email="query-test-user@example.com")

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

    def test_users_requires_auth(self):
        self.logout()
        content = self.query_check(self.Query.USERS, assert_errors=True)
        assert content is not None

    def test_users_paginated(self):
        self.force_login(self.user)
        content = self.query_check(self.Query.USERS, variables={"pagination": {"limit": 10, "offset": 0}})
        users = content["data"]["users"]
        assert "count" in users
        assert "results" in users
