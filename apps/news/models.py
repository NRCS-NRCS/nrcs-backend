from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django_choices_field import IntegerChoicesField
from mdeditor.fields import MDTextField

from apps.common.models import StatusEnum, UserResource
from apps.strategic.models import StrategicDirectives
from utils.common import (
    MAX_IMAGE_FILE_SIZE,
    MAX_NEWS_ATTACHMENT_SIZE,
    unique_slugify,
    validate_file_size,
)
from utils.embed import validate_embeds


# Create your models here.
class News(UserResource):
    title = models.CharField(max_length=255)
    content = MDTextField(blank=True, null=True)
    published_date = models.DateField()
    directive = models.ForeignKey(
        StrategicDirectives,
        on_delete=models.CASCADE,
        related_name="news",
        null=True,
        blank=True,
    )
    slug = models.SlugField(unique=True, max_length=250, blank=True, verbose_name=_("Slug"))
    cover_image = models.ImageField(upload_to="news/", null=True, blank=True)
    status = IntegerChoicesField(choices_enum=StatusEnum, default=StatusEnum.DRAFT)
    is_highlighted = models.BooleanField(default=False)
    show_in_popup = models.BooleanField(default=False)

    def clean(self):
        if self.cover_image:
            validate_file_size(self.cover_image, MAX_IMAGE_FILE_SIZE)
        validate_embeds(self.content)
        return super().clean()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(self, slugify(self.title))
        super().save(*args, **kwargs)
        # Only one news item may be shown in the popup at a time; enabling it here
        # clears the flag on every other news item.
        if self.show_in_popup:
            News.objects.exclude(pk=self.pk).filter(show_in_popup=True).update(show_in_popup=False)

    def __str__(self):
        return self.title

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        verbose_name = _("News")
        verbose_name_plural = _("News")


class ActionLink(models.Model):
    url = models.URLField()
    label = models.CharField(max_length=255)
    news = models.ForeignKey(News, on_delete=models.SET_NULL, null=True, blank=True, related_name="action_links")

    def __str__(self):
        return self.label


class NewsAttachment(models.Model):
    MAX_ATTACHMENTS_PER_NEWS = 50

    file = models.FileField(upload_to="news/attachments/")
    order = models.PositiveIntegerField()
    label = models.CharField(max_length=255, blank=True)
    news = models.ForeignKey(News, on_delete=models.SET_NULL, null=True, blank=True, related_name="attachments")

    class Meta:
        ordering = ["order"]
        constraints = [
            # Deferred so a reorder can swap two rows inside one transaction without
            # tripping the constraint on the intermediate state.
            models.UniqueConstraint(
                fields=["news", "order"],
                name="unique_attachment_order_per_news",
                deferrable=models.Deferrable.DEFERRED,
            ),
        ]

    def __str__(self):
        return self.label or f"Attachment {self.order}"

    def clean(self):
        if self.file:
            validate_file_size(self.file, MAX_NEWS_ATTACHMENT_SIZE)
        return super().clean()


class KeyStat(models.Model):
    MAX_FEATURED_PER_NEWS = 4

    order = models.PositiveIntegerField()
    title = models.CharField(max_length=255)
    stat = models.IntegerField()
    featured = models.BooleanField(default=False)
    news = models.ForeignKey(News, on_delete=models.SET_NULL, null=True, blank=True, related_name="key_stats")

    class Meta:
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(
                fields=["news", "order"],
                name="unique_key_stat_order_per_news",
                deferrable=models.Deferrable.DEFERRED,
            ),
        ]

    def __str__(self):
        return self.title
