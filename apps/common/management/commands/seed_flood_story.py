"""Load the Bhote Koshi flood news story, with real photos, files and figures.

The story body lives next to its assets so it can be edited as plain markdown::

    <assets-dir>/story.md          the article, with ``asset:`` image references
    <assets-dir>/photos/           Nepal Red Cross field photographs
    <assets-dir>/satellite/        satellite imagery and maps
    <assets-dir>/docs/             situation reports attached to the story

Inside ``story.md`` an image is written as a normal markdown image whose target
is a path into the assets directory::

    ![Alt text](asset:photos/street-buried-in-silt.jpg)

Each referenced file is uploaded through the configured storage into the same
folder the markdown editor uploads to, and the reference is rewritten to the
stored URL -- so the saved content is exactly what an editor would have
produced by hand.

Running the command again replaces the previously loaded copy of the story.
"""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.common.models import StatusEnum
from apps.news.models import ActionLink, KeyStat, News, NewsAttachment
from apps.strategic.models import StrategicDirectives

TITLE = "Bhote Koshi flood, one week on: what happened in Rasuwa and Nuwakot, and how the Red Cross is responding"
PUBLISHED_DATE = date(2026, 9, 3)
COVER_IMAGE = "photos/trishuli-valley-buried-in-silt.jpg"

# ``asset:<path>`` inside a markdown image or link target.
ASSET_REF_RE = re.compile(r"\(asset:([^)\s]+)\)")
# The storage-relative name of an already-uploaded inline image, whatever MEDIA_URL is.
EDITOR_IMAGE_RE = re.compile(r"\]\((?:[^)\s]*/)?(editor/[^)\s]+)\)")

KEY_STATS = [
    ("People affected across six districts", 1_600_000, True),
    ("Lives lost in Nepal (NDRRMA, 2 September)", 1_114, True),
    ("People still missing", 4_500, True),
    ("People rescued", 11_814, True),
    ("Households needing immediate relief", 10_000, False),
    ("Bridges damaged", 41, False),
]

ACTION_LINKS = [
    ("Follow the IFRC emergency operation", "https://www.ifrc.org/emergency/nepal-flash-floods-2026"),
    ("WHO health situation updates", "https://www.who.int/nepal/emergencies/2026-rasuwa-flash-floods"),
    (
        "How the Red Cross is responding",
        "https://www.redcross.org.uk/stories/disasters-and-emergencies/world/nepal-flash-floods-2026",
    ),
]

ATTACHMENTS = [
    ("docs/nrcs-rasuwa-situation-update-1-26-aug-2026.pdf", "NRCS Rasuwa Flood Situation Update 1 (26 August 2026)"),
    ("docs/nrcs-rasuwa-situation-update-2-27-aug-2026.pdf", "NRCS Rasuwa Flood Situation Update 2 (27 August 2026)"),
    ("docs/nrcs-rasuwa-situation-update-3-28-aug-2026.pdf", "NRCS Rasuwa Flood Situation Update 3 (28 August 2026)"),
    ("docs/ecdm-nepal-glof-27-aug-2026.pdf", "ERCC emergency mapping: Nepal GLOF (27 August 2026)"),
    ("docs/ecdm-nepal-floods-02-sep-2026.pdf", "ERCC emergency mapping: Nepal floods (2 September 2026)"),
]


class Command(BaseCommand):
    help = "Create the Bhote Koshi flood news story from the assets in data/seed_assets/flood."

    def add_arguments(self, parser):
        parser.add_argument(
            "--assets-dir",
            default=str(Path(settings.BASE_DIR) / "data" / "seed_assets" / "flood"),
            help="Directory holding story.md, photos/, satellite/ and docs/.",
        )
        parser.add_argument("--author", default=None, help="Username to record as author (default: a superuser).")
        parser.add_argument("--draft", action="store_true", help="Save as a draft instead of publishing.")
        parser.add_argument("--no-popup", action="store_true", help="Do not show the story in the homepage popup.")

    def handle(self, *args, **options):
        assets_dir = Path(options["assets_dir"])
        story_path = assets_dir / "story.md"
        if not story_path.is_file():
            raise CommandError(f"story.md not found in {assets_dir}")

        author = self._resolve_author(options["author"])
        body = story_path.read_text()

        with transaction.atomic():
            removed = self._remove_previous()
            content, uploaded = self._upload_inline_images(body, assets_dir)
            news = self._create_news(content, author, assets_dir, options)
            self._create_key_stats(news)
            self._create_action_links(news)
            attached = self._create_attachments(news, assets_dir)

        if removed:
            self.stdout.write(f"Replaced {removed} previously loaded copy of the story.")
        self.stdout.write(f"Inline images uploaded: {uploaded}")
        self.stdout.write(f"Attachments:            {attached}")
        self.stdout.write(f"Key stats:              {len(KEY_STATS)}")
        self.stdout.write(f"Action links:           {len(ACTION_LINKS)}")
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"News #{news.pk} created: {news.title}"))
        self.stdout.write(f"Slug: {news.slug}")

    # -- helpers ----------------------------------------------------------

    def _resolve_author(self, username: str | None) -> User:
        if username:
            try:
                return User.objects.get(username=username)
            except User.DoesNotExist as exc:
                raise CommandError(f"no user named {username!r}") from exc
        author = User.objects.filter(is_superuser=True).order_by("pk").first() or User.objects.order_by("pk").first()
        if author is None:
            raise CommandError("no users in the database -- run `seed_fake_data` or create a superuser first")
        return author

    def _remove_previous(self) -> int:
        """Drop an earlier copy of this story, children first.

        The children point at News with ``on_delete=SET_NULL``, so deleting the
        news alone would leave orphaned attachments and key stats behind.
        """
        previous = list(News.objects.filter(title=TITLE))
        if not previous:
            return 0
        ActionLink.objects.filter(news__in=previous).delete()
        KeyStat.objects.filter(news__in=previous).delete()
        # The inline images were uploaded by an earlier run of this command, so drop
        # them too -- otherwise every re-run leaves a full set of orphans behind.
        for news in previous:
            for name in EDITOR_IMAGE_RE.findall(news.content or ""):
                default_storage.delete(name)
        for attachment in NewsAttachment.objects.filter(news__in=previous):
            attachment.file.delete(save=False)
            attachment.delete()
        for news in previous:
            news.cover_image.delete(save=False)
            news.delete()
        return len(previous)

    def _upload_inline_images(self, body: str, assets_dir: Path) -> tuple[str, int]:
        """Store every ``asset:`` image and rewrite the reference to its URL."""
        uploaded: dict[str, str] = {}

        def replace(match: re.Match) -> str:
            relative_path = match.group(1)
            if relative_path not in uploaded:
                source = assets_dir / relative_path
                if not source.is_file():
                    raise CommandError(f"asset referenced by story.md is missing: {source}")
                saved_path = default_storage.save(
                    f"editor/{source.name}",
                    ContentFile(source.read_bytes(), name=source.name),
                )
                uploaded[relative_path] = default_storage.url(saved_path)
            return f"({uploaded[relative_path]})"

        return ASSET_REF_RE.sub(replace, body), len(uploaded)

    # -- creators ---------------------------------------------------------

    def _create_news(self, content: str, author: User, assets_dir: Path, options) -> News:
        cover = assets_dir / COVER_IMAGE
        if not cover.is_file():
            raise CommandError(f"cover image not found: {cover}")
        directive = StrategicDirectives.objects.filter(title__icontains="Disaster Risk Management").first()
        return News.objects.create(
            title=TITLE,
            content=content,
            published_date=PUBLISHED_DATE,
            directive=directive,
            cover_image=ContentFile(cover.read_bytes(), name=cover.name),
            status=StatusEnum.DRAFT if options["draft"] else StatusEnum.PUBLISHED,
            is_highlighted=True,
            show_in_popup=not options["no_popup"],
            created_by=author,
            modified_by=author,
        )

    def _create_key_stats(self, news: News):
        for order, (title, value, featured) in enumerate(KEY_STATS, start=1):
            KeyStat.objects.create(order=order, title=title, stat=value, featured=featured, news=news)

    def _create_action_links(self, news: News):
        for label, url in ACTION_LINKS:
            ActionLink.objects.create(url=url, label=label, news=news)

    def _create_attachments(self, news: News, assets_dir: Path) -> int:
        order = 0
        for relative_path, label in ATTACHMENTS:
            source = assets_dir / relative_path
            if not source.is_file():
                self.stdout.write(self.style.WARNING(f"attachment missing, skipped: {source}"))
                continue
            order += 1
            NewsAttachment.objects.create(
                file=ContentFile(source.read_bytes(), name=source.name),
                order=order,
                label=label,
                news=news,
            )
        return order
