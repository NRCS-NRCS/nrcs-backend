from apps.common.serializers import UserResourceSerializer
from apps.vacancy.models import JobVacancy


class JobVacancySerializer(UserResourceSerializer[JobVacancy]):
    class Meta:
        model = JobVacancy
        fields = [
            "title",
            "file",
            "position",
            "description",
            "number_of_vacancies",
            "expiry_date",
            "department",
            "is_archived",
            "published_at",
        ]
        read_only_fields = [
            "created_by",
            "modified_by",
        ]
