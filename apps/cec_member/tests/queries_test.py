from apps.cec_member.factories import CecMemberFactory
from apps.cec_member.models import CecMemberTypeEnum
from main.tests.base_test import TestCase


class TestCecMemberQuery(TestCase):
    class Query:
        CEC_MEMBERS = """
          query cecMembers($filters: CecMemberFilter, $order: CecMemberOrder) {
            cecMembers(filters: $filters, order: $order) {
                totalCount
                results {
                  id
                  name
                  memberType
                  designation
                  isActive
                  orderIndex
                }
            }
          }
        """

    def test_cec_members_query(self):
        chairperson = CecMemberFactory.create(
            name="Chair",
            member_type=CecMemberTypeEnum.OFFICE_BEARER,
            designation="Chairperson",
            order_index=1,
        )
        member = CecMemberFactory.create(name="Member", order_index=0)
        CecMemberFactory.create(name="Hidden", is_active=False, order_index=2)

        content = self.query_check(
            self.Query.CEC_MEMBERS,
            variables={
                "filters": {"isActive": {"exact": True}},
                "order": {"orderIndex": "ASC"},
            },
        )
        assert content["data"]["cecMembers"] == dict(
            totalCount=2,
            results=[
                dict(
                    id=self.gID(item.id),
                    name=item.name,
                    memberType=self.genum(item.member_type),
                    designation=item.designation,
                    isActive=True,
                    orderIndex=item.order_index,
                )
                for item in [member, chairperson]
            ],
        ), content
