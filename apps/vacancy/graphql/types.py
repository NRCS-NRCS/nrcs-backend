import strawberry
import strawberry_django

from apps.vacancy.models import JobVacancy
from utils.graphql.types import DjangoFileType


@strawberry_django.type(JobVacancy)
class JobVacancyType:
    id: strawberry.ID
    title: strawberry.auto
    file: DjangoFileType
    description: strawberry.auto
    position: strawberry.auto
    number_of_vacancies: strawberry.auto
    expiry_date: strawberry.auto
    is_archived: strawberry.auto
    published_at: strawberry.auto
