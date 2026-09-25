from apps.cec_member.factories import CecMemberFactory
from apps.cec_member.models import CecMember, CecMemberTypeEnum
from apps.strategic.factories import UserFactory
from main.tests.base_test import TestCase


class TestCecMemberMutation(TestCase):
    class Mutation:
        CREATE_CEC_MEMBER = """
          mutation createCecMember($data: CecMemberCreateInput!) {
              createCecMember(data: $data) {
                  ... on CecMemberTypeMutationResponseType {
                       errors
                       ok
                       result {
                          id
                          name
                          memberType
                          designation
                          email
                          orderIndex
                       }
                  }
              }
          }
        """

        UPDATE_CEC_MEMBER = """
            mutation updateCecMember($pk: ID!, $data: CecMemberUpdateInput!) {
                updateCecMember(data: $data, pk: $pk) {
                    ... on CecMemberTypeMutationResponseType {
                       errors
                       ok
                       result {
                         id
                         name
                         isActive
                       }
                    }
                }
            }
        """

        REORDER_CEC_MEMBER = """
            mutation reorderCecMember($data: CecMemberReorderInput!) {
                reorderCecMember(data: $data) {
                    ... on CecMemberTypeListMutationResponseType {
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

    def test_create_cec_member(self):
        CecMemberFactory.create(order_index=4)
        data = {
            "name": "Dr. Test Member",
            "memberType": self.genum(CecMemberTypeEnum.OFFICE_BEARER),
            "designation": "Chairperson",
            "email": "test@example.com",
        }

        content = self.query_check(self.Mutation.CREATE_CEC_MEMBER, variables={"data": data})
        assert content["data"]["createCecMember"] == {}, content
        assert not CecMember.objects.filter(name=data["name"]).exists()

        self.force_login(self.user)
        content = self.query_check(self.Mutation.CREATE_CEC_MEMBER, variables={"data": data})
        resp_data = content["data"]["createCecMember"]
        assert resp_data == self.g_mutation_response(
            ok=True,
            result=dict(
                id=resp_data["result"]["id"],
                **data,
                orderIndex=5,
            ),
        ), content

        content = self.query_check(
            self.Mutation.CREATE_CEC_MEMBER,
            variables={
                "data": {
                    **data,
                    "designation": None,
                    "email": None,
                    "secondaryEmail": None,
                    "address": None,
                    "contactNumber": None,
                },
            },
        )
        resp_data = content["data"]["createCecMember"]
        assert resp_data["ok"] is True, content
        assert resp_data["result"]["email"] is None
        assert resp_data["result"]["designation"] is None

        # Invalid email is rejected
        content = self.query_check(
            self.Mutation.CREATE_CEC_MEMBER,
            variables={"data": {**data, "email": "not-an-email"}},
        )
        assert content["data"]["createCecMember"]["ok"] is False, content

    def test_update_cec_member(self):
        member = CecMemberFactory.create(name="Old name")
        self.force_login(self.user)
        content = self.query_check(
            self.Mutation.UPDATE_CEC_MEMBER,
            variables={
                "pk": self.gID(member.id),
                "data": {"name": "New name", "isActive": False},
            },
        )
        assert content["data"]["updateCecMember"] == self.g_mutation_response(
            ok=True,
            result=dict(id=self.gID(member.id), name="New name", isActive=False),
        ), content

    def test_reorder_cec_member(self):
        first, second, third = [CecMemberFactory.create(order_index=index) for index in range(3)]
        self.force_login(self.user)
        content = self.query_check(
            self.Mutation.REORDER_CEC_MEMBER,
            variables={
                "data": {
                    "movedId": self.gID(third.id),
                    "targetId": self.gID(first.id),
                    "position": "BEFORE",
                },
            },
        )
        assert content["data"]["reorderCecMember"]["ok"] is True, content
        assert list(CecMember.objects.order_by("order_index").values_list("id", flat=True)) == [
            third.id,
            first.id,
            second.id,
        ]
