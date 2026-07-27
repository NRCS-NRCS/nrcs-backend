import strawberry
import strawberry_django
from strawberry.file_uploads import Upload

from apps.vacancy.models import JobVacancy


@strawberry_django.input(JobVacancy)
class JobVacancyCreateInput:
    title: strawberry.auto
    description: strawberry.auto
    position: strawberry.auto
    number_of_vacancies: strawberry.auto
    expiry_date: strawberry.auto
    is_archived: strawberry.auto
    published_at: strawberry.auto
    department: strawberry.ID | None
    file: Upload


@strawberry_django.partial(JobVacancy)
class JobVacancyUpdateInput:
    title: strawberry.auto
    description: strawberry.auto
    position: strawberry.auto
    number_of_vacancies: strawberry.auto
    expiry_date: strawberry.auto
    is_archived: strawberry.auto
    published_at: strawberry.auto
    department: strawberry.ID | None
    file: Upload | None


@strawberry_django.input(JobVacancy)
class JobVacancyDeleteInput:
    id: strawberry.ID
