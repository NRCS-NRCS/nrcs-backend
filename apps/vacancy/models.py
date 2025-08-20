from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import UserResource


class JobVacancy(UserResource):
    title = models.CharField(max_length=255, verbose_name=_("Vacancy Title"))
    file = models.FileField(upload_to="job_vacancy/", verbose_name=_("Vacancy File"))
    position = models.CharField(max_length=255, verbose_name=_("Vacancy Position"))
    description = models.TextField(verbose_name=_("Vacancy Description"))
    number_of_vacancies = models.PositiveIntegerField()
    expiry_date = models.DateField()
    department = models.ForeignKey(
        "department.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Department"),
    )
    is_archived = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.position} - {self.id}"

    class Meta(UserResource.Meta):
        verbose_name = _("Job Vacancy")
        verbose_name_plural = _("Job Vacancies")
        ordering = ("-created_at",)
        db_table = "job_vacancy"
