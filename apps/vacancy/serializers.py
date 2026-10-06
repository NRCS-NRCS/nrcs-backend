import typing

from apps.common.serializers import UserResourceSerializer
from apps.vacancy.models import JobVacancy
from utils.common import validate_expiry_date


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

    @typing.override
    def validate(self, attrs):
        attrs = super().validate(attrs)
        validate_expiry_date(attrs, self.instance, "published_at")
        return attrs
