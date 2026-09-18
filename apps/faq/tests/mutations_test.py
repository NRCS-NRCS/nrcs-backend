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

    def test_create_faq_appended_to_end(self):
        # Existing FAQs occupy 0..2; a newly created FAQ must land after them.
        FaqFactory.create(question="Q1", answer="A1", order_index=0)
        FaqFactory.create(question="Q2", answer="A2", order_index=1)
        FaqFactory.create(question="Q3", answer="A3", order_index=2)

        data = {
            "question": "What is your return policy?",
            "answer": "You can return any item within 30 days of purchase.",
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
        # Appended to the end: max existing index (2) + 1.
        assert resp_data["result"]["orderIndex"] == 3, content

    def test_create_first_faq_starts_at_zero(self):
        data = {"question": "First?", "answer": "Yes."}

        self.force_login(self.user)
        content = self.query_check(
            self.Mutation.CREATE_FAQ,
            variables={"data": data},
        )
        resp_data = content["data"]["createFaq"]
        assert resp_data["ok"] is True, content
        assert resp_data["result"]["orderIndex"] == 0, content

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

    def test_reorder_faq_move_before(self):
        faq1 = FaqFactory.create(question="Q1", answer="A1", order_index=0)
        faq2 = FaqFactory.create(question="Q2", answer="A2", order_index=1)
        faq3 = FaqFactory.create(question="Q3", answer="A3", order_index=2)

        self.force_login(self.user)
        content = self.query_check(
            self.Mutation.REORDER_FAQ,
            variables={
                # Move faq3 to sit before faq1 -> [faq3, faq1, faq2].
                "data": {
                    "movedId": self.gID(faq3.id),
                    "targetId": self.gID(faq1.id),
                    "position": "BEFORE",
                },
            },
        )
        resp_data = content["data"]["reorderFaq"]
        assert resp_data["ok"] is True, content
        assert resp_data["errors"] is None, content
        order_by_id = {item["id"]: item["orderIndex"] for item in resp_data["result"]}
        assert order_by_id[self.gID(faq3.id)] == 0, content
        assert order_by_id[self.gID(faq1.id)] == 1, content
        assert order_by_id[self.gID(faq2.id)] == 2, content

    def test_reorder_faq_move_after(self):
        faq1 = FaqFactory.create(question="Q1", answer="A1", order_index=0)
        faq2 = FaqFactory.create(question="Q2", answer="A2", order_index=1)
        faq3 = FaqFactory.create(question="Q3", answer="A3", order_index=2)

        self.force_login(self.user)
        content = self.query_check(
            self.Mutation.REORDER_FAQ,
            variables={
                # Move faq1 to sit after faq3 -> [faq2, faq3, faq1].
                "data": {
                    "movedId": self.gID(faq1.id),
                    "targetId": self.gID(faq3.id),
                    "position": "AFTER",
                },
            },
        )
        resp_data = content["data"]["reorderFaq"]
        assert resp_data["ok"] is True, content
        assert resp_data["errors"] is None, content
        order_by_id = {item["id"]: item["orderIndex"] for item in resp_data["result"]}
        assert order_by_id[self.gID(faq2.id)] == 0, content
        assert order_by_id[self.gID(faq3.id)] == 1, content
        assert order_by_id[self.gID(faq1.id)] == 2, content

    def test_reorder_faq_unknown_id(self):
        faq1 = FaqFactory.create(question="Q1", answer="A1", order_index=0)
        FaqFactory.create(question="Q2", answer="A2", order_index=1)

        self.force_login(self.user)
        content = self.query_check(
            self.Mutation.REORDER_FAQ,
            variables={
                "data": {
                    "movedId": self.gID(faq1.id),
                    "targetId": self.gID(9999),
                    "position": "AFTER",
                },
            },
        )
        resp_data = content["data"]["reorderFaq"]
        assert resp_data["ok"] is False, content
        assert resp_data["errors"] is not None, content
        # Nothing updated on rejection.
        faq1.refresh_from_db()
        assert faq1.order_index == 0, content

    def test_reorder_faq_self_move_rejected(self):
        faq1 = FaqFactory.create(question="Q1", answer="A1", order_index=0)
        FaqFactory.create(question="Q2", answer="A2", order_index=1)

        self.force_login(self.user)
        content = self.query_check(
            self.Mutation.REORDER_FAQ,
            variables={
                "data": {
                    "movedId": self.gID(faq1.id),
                    "targetId": self.gID(faq1.id),
                    "position": "AFTER",
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
                "data": {
                    "movedId": self.gID(faq2.id),
                    "targetId": self.gID(faq1.id),
                    "position": "BEFORE",
                },
            },
        )
        # IsStaff() denies -> no successful reorder.
        resp_data = content["data"]["reorderFaq"]
        assert resp_data.get("ok") is not True, content
        faq1.refresh_from_db()
        assert faq1.order_index == 0, content
