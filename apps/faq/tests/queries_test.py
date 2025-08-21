from apps.faq.factories import FaqFactory
from apps.strategic.factories import UserFactory
from main.tests.base_test import TestCase


class TestFaqQuery(TestCase):
    class Query:
        FAQ = """
          query faq($order: FaqOrder) {
            faqs(order: $order)
               {
                id
                question
                answer
                orderIndex
              }


          }
        """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = UserFactory.create(username="nrcs-test")

    def test_faq_query(self):
        def _query():
            return self.query_check(
                self.Query.FAQ,
                variables={
                    "order": {"id": "ASC"},
                },
            )

        faq_items = [
            FaqFactory.create(
                question="Question One",
                answer="Answer One",
                order_index=1,
            ),
            FaqFactory.create(
                question="Question Two",
                answer="Answer Two",
                order_index=2,
            ),
        ]

        content = _query()
        assert content["data"] == {
            "faqs": [
                dict(
                    id=self.gID(faq.id),
                    question=faq.question,
                    answer=faq.answer,
                    orderIndex=faq.order_index,
                )
                for faq in faq_items
            ],
        }, content
