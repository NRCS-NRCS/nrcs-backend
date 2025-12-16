from apps.faq.factories import FaqFactory
from apps.faq.models import Faq
from apps.strategic.factories import UserFactory
from main.tests.base_test import TestCase


class TestFaqMutation(TestCase):
    class Mutation:
        CREATE_FAQ = """
          mutation createFaq($data: FaqCreateInput!) {
              createFaq(data: $data) {
                  ... on FaqTypeMutationResponseType {
                       errors
                       ok
                       result {
                          id
                          question
                          answer
                          orderIndex
                       }
                  }
              }
          }
        """

        UPDATE_FAQ = """
            mutation updateFaq($pk: ID!, $data: FaqUpdateInput!) {
                updateFaq(data: $data, pk: $pk) {
                    ... on FaqTypeMutationResponseType {
                       errors
                       ok
                       result {
                         id
                         question
                         answer
                         orderIndex
                       }
                    }
                }
            }
        """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = UserFactory.create(username="nrcs-test")

    def test_create_faq(self):
        data = {
            "question": "What is your return policy?",
            "answer": "You can return any item within 30 days of purchase.",
            "orderIndex": 1,
        }

        self.force_login(self.user)
        content = self.query_check(
            self.Mutation.CREATE_FAQ,
            variables={
                "data": data,
            },
        )
        resp_data = content["data"]["createFaq"]
        assert resp_data["ok"] is True, content
        assert resp_data["errors"] is None, content
        assert resp_data["result"]["question"] == data["question"], content
        assert resp_data["result"]["answer"] == data["answer"], content

    def test_update_faq(self):
        faq = FaqFactory.create(
            question="Old Question",
            answer="Old Answer",
            order_index=1,
        )

        data = {
            "question": "Updated Question",
            "answer": "Updated Answer",
            "orderIndex": 2,
        }

        self.force_login(self.user)
        content = self.query_check(
            self.Mutation.UPDATE_FAQ,
            variables={
                "pk": self.gID(faq.id),
                "data": data,
            },
        )
        resp_data = content["data"]["updateFaq"]
        assert resp_data["ok"] is True, content
        assert resp_data["errors"] is None, content
        assert resp_data["result"]["question"] == data["question"], content
        assert resp_data["result"]["answer"] == data["answer"], content
