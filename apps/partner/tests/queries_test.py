from django.core.files.uploadedfile import SimpleUploadedFile

from apps.partner.factories import PartnerFactory
from apps.partner.models import PartnerScopeEnum
from apps.strategic.factories import UserFactory
from main.tests.base_test import TestCase


class TestPartnerQuery(TestCase):
    class Query:
        PARTNERS = """
          query partners($order: PartnerOrder) {
            partners(order: $order) {
                results {
                  id
                  title
                  image{
                    url
                  }
                  scope
                }
            }
          }
        """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = UserFactory.create(username="nrcs-test")

    def test_partners_query(self):
        def _query():
            return self.query_check(
                self.Query.PARTNERS,
                variables={
                    "order": {"id": "ASC"},
                },
            )

        partner_items = [
            PartnerFactory.create(
                title="Partner one",
                scope=PartnerScopeEnum.LOCAL,
                image=SimpleUploadedFile("partner1.jpg", b"file_content"),
            ),
            PartnerFactory.create(
                title="Partner two",
                scope=PartnerScopeEnum.LOCAL,
                image=SimpleUploadedFile("partner1.jpg", b"file_content"),
            ),
        ]

        content = _query()
        assert content["data"]["partners"]["results"] == [
            dict(
                id=self.gID(partner.id),
                title=partner.title,
                image=dict(
                    url=self.get_media_url(partner.image.name),
                ),
                scope=self.genum(partner.scope),
            )
            for partner in partner_items
        ], content
