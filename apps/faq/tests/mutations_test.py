from apps.faq.factories import FaqFactory
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

        REORDER_FAQ = """
            mutation reorderFaq($data: FaqReorderInput!) {
                reorderFaq(data: $data) {
                    ... on FaqTypeListMutationResponseType {
                       errors
                       ok
                       result {
                         id
                         orderIndex
                       }
                    }
                }
            }
        """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = UserFactory.create(username="nrcs-test", is_staff=True)

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

    def test_reorder_faq(self):
        faq1 = FaqFactory.create(question="Q1", answer="A1", order_index=0)
        faq2 = FaqFactory.create(question="Q2", answer="A2", order_index=1)
        faq3 = FaqFactory.create(question="Q3", answer="A3", order_index=2)

        self.force_login(self.user)
        content = self.query_check(
            self.Mutation.REORDER_FAQ,
            variables={
                "data": {
                    "orderedIds": [self.gID(faq3.id), self.gID(faq1.id), self.gID(faq2.id)],
                },
            },
        )
        resp_data = content["data"]["reorderFaq"]
        assert resp_data["ok"] is True, content
        assert resp_data["errors"] is None, content
        # order_index is recomputed from the position in the provided list.
        order_by_id = {item["id"]: item["orderIndex"] for item in resp_data["result"]}
        assert order_by_id[self.gID(faq3.id)] == 0, content
        assert order_by_id[self.gID(faq1.id)] == 1, content
        assert order_by_id[self.gID(faq2.id)] == 2, content

    def test_reorder_faq_missing_id(self):
        faq1 = FaqFactory.create(question="Q1", answer="A1", order_index=0)
        faq2 = FaqFactory.create(question="Q2", answer="A2", order_index=1)

        self.force_login(self.user)
        content = self.query_check(
            self.Mutation.REORDER_FAQ,
            variables={
                # faq2 omitted -> set mismatch, must be rejected.
                "data": {"orderedIds": [self.gID(faq1.id)]},
            },
        )
        resp_data = content["data"]["reorderFaq"]
        assert resp_data["ok"] is False, content
        assert resp_data["errors"] is not None, content
        # Nothing updated on rejection.
        faq2.refresh_from_db()
        assert faq2.order_index == 1, content

    def test_reorder_faq_unknown_id(self):
        faq1 = FaqFactory.create(question="Q1", answer="A1", order_index=0)
        faq2 = FaqFactory.create(question="Q2", answer="A2", order_index=1)

        self.force_login(self.user)
        content = self.query_check(
            self.Mutation.REORDER_FAQ,
            variables={
                "data": {
                    "orderedIds": [self.gID(faq1.id), self.gID(faq2.id), self.gID(9999)],
                },
            },
        )
        resp_data = content["data"]["reorderFaq"]
        assert resp_data["ok"] is False, content
        assert resp_data["errors"] is not None, content

    def test_reorder_faq_duplicate_id(self):
        faq1 = FaqFactory.create(question="Q1", answer="A1", order_index=0)
        faq2 = FaqFactory.create(question="Q2", answer="A2", order_index=1)

        self.force_login(self.user)
        content = self.query_check(
            self.Mutation.REORDER_FAQ,
            variables={
                "data": {
                    "orderedIds": [self.gID(faq1.id), self.gID(faq1.id), self.gID(faq2.id)],
                },
            },
        )
        resp_data = content["data"]["reorderFaq"]
        assert resp_data["ok"] is False, content
        assert resp_data["errors"] is not None, content

    def test_reorder_faq_requires_staff(self):
        non_staff = UserFactory.create(username="nrcs-non-staff", is_staff=False)
        faq1 = FaqFactory.create(question="Q1", answer="A1", order_index=0)
        faq2 = FaqFactory.create(question="Q2", answer="A2", order_index=1)

        self.force_login(non_staff)
        content = self.query_check(
            self.Mutation.REORDER_FAQ,
            variables={
                "data": {"orderedIds": [self.gID(faq2.id), self.gID(faq1.id)]},
            },
        )
        # IsStaff() denies -> no successful reorder.
        resp_data = content["data"]["reorderFaq"]
        assert resp_data.get("ok") is not True, content
        faq1.refresh_from_db()
        assert faq1.order_index == 0, content
