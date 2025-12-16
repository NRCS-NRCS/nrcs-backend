from apps.department.factories import DepartmentFactory
from apps.project.factories import ProjectFactory
from apps.project.models import Project
from apps.strategic.factories import StrategicDirectivesFactory, UserFactory
from main.tests.base_test import TestCase


class TestProjectMutation(TestCase):
    class Mutation:
        CREATE_PROJECT = """
          mutation createProject($data: ProjectCreateInput!) {
            createProject(data: $data) {
                ... on OperationInfo {
                  __typename
                  messages {
                    code
                    field
                    kind
                    message
                  }
                }
                ... on ProjectTypeMutationResponseType {
                   errors
                   ok
                   result {
                     id
                     title
                     description
                     department {
                       id
                       title
                     }
                   }
                }
            }
          }
        """
        UPDATE_PROJECT = """
            mutation updateProject($pk: ID!, $data: ProjectUpdateInput!) {
                updateProject(data: $data, pk: $pk) {
                    ... on OperationInfo {
                      __typename
                      messages {
                        code
                        field
                        kind
                        message
                      }
                    }
                    ... on ProjectTypeMutationResponseType {
                       errors
                       ok
                       result {
                         id
                         title
                         description
                         department {
                           id
                           title
                         }
                       }
                    }
                }
            }
        """
        DELETE_PROJECT = """
            mutation deleteProject($data: ProjectDeleteInput!) {
                deleteProject(data: $data) {
                    ... on OperationInfo {
                      __typename
                      messages {
                        code
                        field
                        kind
                        message
                      }
                    }
                    ... on ProjectType{
                         id
                         title
                         description
                    }
                }
            }
        """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = UserFactory.create(username="nrcs-test")

    def test_create_project(self):
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

        data = {
            "title": "New Project",
            "description": "Project Description",
            "department": self.gID(department.id),
        }

        self.force_login(self.user)
        content = self.query_check(
            self.Mutation.CREATE_PROJECT,
            variables={
                "data": data,
            },
        )

        assert content["data"]["createProject"]["errors"] is None, content
        assert {
            "id": content["data"]["createProject"]["result"]["id"],
            "title": "New Project",
            "description": "Project Description",
            "department": {
                "id": self.gID(department.id),
                "title": department.title,
            },
        } == {
            "id": content["data"]["createProject"]["result"]["id"],
            "title": data["title"],
            "description": data["description"],
            "department": {
                "id": self.gID(department.id),
                "title": department.title,
            },
        }, content

    def test_update_project(self):
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

        project = ProjectFactory.create(
            title="Old Project",
            description="Old Description",
            department=department,
        )
        data = {
            "title": "Updated Project",
            "description": "Updated Description",
        }
        self.force_login(self.user)
        content = self.query_check(
            self.Mutation.UPDATE_PROJECT,
            variables={
                "pk": self.gID(project.id),
                "data": data,
            },
        )
        assert content["data"]["updateProject"]["errors"] is None, content
        assert {
            "id": self.gID(project.id),
            "title": "Updated Project",
            "description": "Updated Description",
            "department": {
                "id": self.gID(department.id),
                "title": department.title,
            },
        } == {
            "id": content["data"]["updateProject"]["result"]["id"],
            "title": data["title"],
            "description": data["description"],
            "department": {
                "id": self.gID(department.id),
                "title": department.title,
            },
        }, content

    def test_delete_project(self):
        project = ProjectFactory.create(
            title="Project title",
            description="To be deleted",
        )

        self.force_login(self.user)
        content = self.query_check(
            self.Mutation.DELETE_PROJECT,
            variables={
                "data": {
                    "id": self.gID(project.id),
                },
            },
        )
        assert content["data"]["deleteProject"]["id"] == self.gID(project.id), content

        # Verify that the project is actually deleted
        assert not Project.objects.filter(id=project.id).exists()
