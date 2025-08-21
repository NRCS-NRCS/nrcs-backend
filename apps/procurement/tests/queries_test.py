from apps.procurement.factories import ProcurementFactory
from apps.strategic.factories import UserFactory
from main.tests.base_test import TestCase


class TestProcurementQuery(TestCase):
    class Query:
        PROCUREMENT = """
          query procurement($order: ProcurementOrder) {
            procurements(order: $order)
               {
                id
                title
                description
                file {
                  url
                }
                publishedDate
                expiryDate
              }


          }
        """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = UserFactory.create(username="nrcs-test")

    def test_procurement_query(self):
        def _query():
            return self.query_check(
                self.Query.PROCUREMENT,
                variables={
                    "order": {"id": "ASC"},
                },
            )

        procurement_items = [
            ProcurementFactory.create(
                title="Procurement One",
                description="Something",
                file="test.pdf",
                published_date="2023-01-01",
                expiry_date="2023-01-31",
            ),
            ProcurementFactory.create(
                title="Procurement Two",
                description="Something2",
                file="test2.pdf",
                published_date="2023-01-01",
                expiry_date="2023-01-31",
            ),
        ]

        content = _query()
        assert content["data"] == {
            "procurements": [
                dict(
                    id=self.gID(procurement.id),
                    title=procurement.title,
                    description=procurement.description,
                    file={
                        "url": self.get_media_url(procurement.file.name),
                    },
                    publishedDate=procurement.published_date,
                    expiryDate=procurement.expiry_date,
                )
                for procurement in procurement_items
            ],
        }, content
