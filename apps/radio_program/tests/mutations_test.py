from django.core.files.uploadedfile import SimpleUploadedFile

from apps.radio_program.factories import RadioProgramFactory
from apps.radio_program.models import RadioProgram
from apps.strategic.factories import UserFactory
from main.tests.base_test import TestCase


def generate_test_audio_file():
    return SimpleUploadedFile(
        name="test_audio.mp3",
        content=b"Fake MP3 binary content",
        content_type="audio/mpeg",
    )


def graphql_audio_mutation(
    *,
    query_check_func,
    query: str,
    radio_program_data: dict,
    **kwargs,
) -> dict:

    variables = {"data": radio_program_data}
    if pk := kwargs.pop("pk", None):
        variables["pk"] = pk

    with generate_test_audio_file() as audio_file:
        return query_check_func(
            query,
            variables=variables,
            files={
                "audioFile": audio_file,
            },
            map={
                "audioFile": ["variables.data.audioFile"],
            },
            **kwargs,
        )


class TestRadioProgramMutation(TestCase):
    class Mutation:
        CREATE_PARTNER = """
          mutation createRadioProgram($data: RadioProgramCreateInput!) {
              createRadioProgram(data: $data) {
                  ... on RadioProgramTypeMutationResponseType {
                       errors
                       ok
                       result {
                          id
                          title
                          publishedDate
                          createdBy {
                            id
                          }
                       }
                  }
              }
          }
        """

        UPDATE_PARTNER = """
            mutation updateRadioProgram($pk: ID!, $data: RadioProgramUpdateInput!) {
                updateRadioProgram(data: $data, pk: $pk) {
                    ... on RadioProgramTypeMutationResponseType {
                       errors
                       ok
                       result {
                         id
                         title
                         publishedDate
                       }
                    }
                }
            }
        """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = UserFactory.create(username="nrcs-test")

    def test_create_partner(self):
        data = {
            "title": "New RadioProgram",
            "publishedDate": "2024-01-01",
        }

        self.force_login(self.user)
        content = graphql_audio_mutation(
            query_check_func=self.query_check,
            query=self.Mutation.CREATE_PARTNER,
            radio_program_data=data,
        )

        resp_data = content["data"]["createRadioProgram"]
        assert resp_data == self.g_mutation_response(
            ok=True,
            errors=None,
            result=dict(
                id=resp_data["result"]["id"],
                title=data["title"],
                publishedDate=data["publishedDate"],
                createdBy=dict(
                    id=self.gID(self.user.id),
                ),
            ),
        ), content

        # Check the audio file is saved correctly
        partner_id = resp_data["result"]["id"]
        partner = RadioProgram.objects.get(id=self.gID(partner_id))
        assert partner.audio_file, "Audio file should be saved and not empty"

    def test_update_partner(self):
        partner = RadioProgramFactory.create(
            title="Initial Title",
            published_date="2024-01-01",
        )

        data = {
            "title": "Updated RadioProgram Title",
            "publishedDate": "2024-02-01",
        }

        self.force_login(self.user)
        content = self.query_check(
            self.Mutation.UPDATE_PARTNER,
            variables={
                "pk": self.gID(partner.id),
                "data": data,
            },
        )
        resp_data = content["data"]["updateRadioProgram"]
        assert resp_data == self.g_mutation_response(
            ok=True,
            result=dict(
                id=self.gID(partner.id),
                title=data["title"],
                publishedDate=data["publishedDate"],
            ),
        ), content

        # Update with new audio
        content = graphql_audio_mutation(
            query_check_func=self.query_check,
            query=self.Mutation.UPDATE_PARTNER,
            radio_program_data=data,
            pk=self.gID(partner.id),
        )
        resp_data = content["data"]["updateRadioProgram"]
        assert resp_data == self.g_mutation_response(
            ok=True,
            result=dict(
                id=self.gID(partner.id),
                title=data["title"],
                publishedDate=data["publishedDate"],
            ),
        ), content

        # Check THE file should not be empty
        partner.refresh_from_db()
        assert partner.audio_file, "Audio file should be updated and not empty"
