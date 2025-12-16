from apps.department.factories import DepartmentFactory
from apps.strategic.factories import StrategicDirectivesFactory, UserFactory
from main.tests.base_test import TestCase


class TestDepartmentQuery(TestCase):
    class Mutation:
        CREATE_DEPARTMENT = """
          mutation createDepartment($data: DepartmentCreateInput!) {
            createDepartment(data: $data) {
                ... on OperationInfo {
                  __typename
                  messages {
                    code
                    field
                    kind
                    message
                  }
                }
                ... on DepartmentTypeMutationResponseType {
                   errors
                   ok
                   result {
                     id
                     title
                     description
                     contactPersonName
                     contactPersonEmail
                     strategicDirective {
                       id
                       slug
                       title
                       description
                       contactPersonName
                       contactPersonEmail
                     }
                   }
                }
            }
          }
        """

        UPDATE_DEPARTMENT = """
            mutation updateDepartment($pk: ID!, $data: DepartmentUpdateInput!) {
                updateDepartment(data: $data, pk: $pk) {
                    ... on OperationInfo {
                      __typename
                      messages {
                        code
                        field
                        kind
                        message
                      }
                    }
                    ... on DepartmentTypeMutationResponseType {
                       errors
                       ok
                       result {
                         id
                         title
                         description
                         contactPersonName
                         contactPersonEmail
                         strategicDirective {
                           id
                           slug
                           title
                           description
                           contactPersonName
                           contactPersonEmail
                         }
                       }
                    }
                }
            }
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = UserFactory.create(username="nrcs-test")

    def test_create_department(self):
        strategic_directive = StrategicDirectivesFactory.create(
            title="Strategic Directive",
            description="Something",
            contact_person_name="John Doe",
            contact_person_email="johndoe@example.com",
        )

        data = {
            "title": "Department",
            "description": "Something",
            "contactPersonName": "John Doe",
            "contactPersonEmail": "johndoe@example.com",
            "strategicDirective": strategic_directive.pk,
        }

        self.force_login(self.user)
        content = self.query_check(
            self.Mutation.CREATE_DEPARTMENT,
            variables={
                "data": data,
            },
        )
        resp_data = content["data"]["createDepartment"]
        assert resp_data["errors"] is None, content
        assert resp_data["result"]["title"] == data["title"], content
        assert resp_data["result"]["description"] == data["description"], content
        assert (
            resp_data["result"]["strategicDirective"]["id"]
            == self.gID(strategic_directive.id)
        ), content

    def test_update_department(self):
        department = DepartmentFactory.create(
            title="Department One",
            description="Something",
            contact_person_name="John Doe",
            contact_person_email="johndoe@example.com",
            strategic_directive=StrategicDirectivesFactory.create(
                title="Strategic Directive One",
                description="Something",
                contact_person_name="John Doe",
                contact_person_email="johndoe@example.com",
            ),
        )
        new_strategic_directive = StrategicDirectivesFactory.create(
            title="Strategic Directive Two",
            description="Something New",
            contact_person_name="Jane Smith",
            contact_person_email="janesmith@example.com",
        )
        data = {
            "title": "Updated Department",
            "description": "Updated Something",
            "contactPersonName": "Jane Smith",
            "strategicDirective": new_strategic_directive.pk,
        }

        self.force_login(self.user)
        content = self.query_check(
            self.Mutation.UPDATE_DEPARTMENT,
            variables={
                "pk": str(department.id),
                "data": data,
            },
        )

        resp_data = content["data"]["updateDepartment"]
        assert resp_data["errors"] is None, content
        assert resp_data["result"]["title"] == data["title"], content
        assert resp_data["result"]["description"] == data["description"], content
        assert (
            resp_data["result"]["strategicDirective"]["id"]
            == self.gID(new_strategic_directive.id)
        ), content
