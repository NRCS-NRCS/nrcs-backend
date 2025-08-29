from apps.radio_program.factories import RadioProgramFactory
from apps.strategic.factories import UserFactory
from main.tests.base_test import TestCase


class TestRadioProgramQuery(TestCase):
    class Query:
        RADIO_PROGRAMS = """
          query radioProgram($order: RadioProgramOrder) {
            radioProgram(order: $order) {
                id
                title
                audioFile{
                    url
                }
                publishedDate
              }

          }
        """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = UserFactory.create(username="nrcs-test")

    def test_job_vacancies_query(self):
        def _query():
            return self.query_check(
                self.Query.RADIO_PROGRAMS,
                variables={
                    "order": {"id": "ASC"},
                },
            )

        radio_program_items = [
            RadioProgramFactory.create(
                title="Radio Program One",
                audio_file="radio1.mp3",
                published_date="2023-12-31",
            ),
            RadioProgramFactory.create(
                title="Radio Program Two",
                audio_file="radio2.wav",
                published_date="2023-12-31",
            ),
        ]

        content = _query()
        assert content["data"] == {
            "radioProgram": [
                dict(
                    id=self.gID(radio_program.id),
                    title=radio_program.title,
                    audioFile=dict(
                        url=self.get_media_url(radio_program.audio_file.name),
                    ),
                    publishedDate=radio_program.published_date,
                )
                for radio_program in radio_program_items
            ],
        }, content
