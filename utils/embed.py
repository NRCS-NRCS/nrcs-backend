"""Validation helpers for video embeds inside markdown content.

Each video is a self-contained fenced ``embed`` block with three fields. Blocks
are independent — to show several videos, add several blocks::

    ```embed
    url: https://www.facebook.com/reel/1527219472411989
    orientation: vertical
    caption: An optional caption
    ```

Fields:

- ``url`` (required): a single supported YouTube or Facebook video/reel URL.
  Unsupported URLs raise a ``ValidationError`` so they are never stored.
- ``orientation`` (optional): ``horizontal`` or ``vertical``. When omitted it is
  inferred from the URL (reels and YouTube shorts are vertical, everything else
  is horizontal) so the frontend can size the iframe correctly.
- ``caption`` (optional): free text.

Parsing for rendering is handled on the frontend; this module only validates the
blocks on save and exposes :func:`parse_embeds` as the canonical reference for
the format.
"""

import re

from django.core.exceptions import ValidationError

# Matches a fenced ```embed ... ``` block and captures its inner body.
EMBED_BLOCK_RE = re.compile(r"```embed[ \t]*\r?\n(.*?)```", re.DOTALL | re.IGNORECASE)

# YouTube video URLs: watch, youtu.be, embed, shorts and live forms.
YOUTUBE_URL_RE = re.compile(
    r"""^https?://
        (?:(?:www|m)\.)?
        (?:
            youtube\.com/(?:watch\?(?:[^\s]*&)?v=[\w-]{11}
                          |embed/[\w-]{11}
                          |shorts/[\w-]{11}
                          |live/[\w-]{11})
          | youtu\.be/[\w-]{11}
        )
        (?![\w-])[^\s]*$
    """,
    re.IGNORECASE | re.VERBOSE,
)

# Facebook video/reel URLs, plus the fb.watch short form.
FACEBOOK_URL_RE = re.compile(
    r"""^https?://
        (?:
            (?:(?:www|web|m)\.)?facebook\.com/
                (?:
                    watch/?\?(?:[^\s]*&)?v=\d+
                  | reel/\d+
                  | [\w.-]+/videos/(?:[\w.-]+/)?\d+
                  | video\.php\?(?:[^\s]*&)?v=\d+
                )
          | fb\.watch/[\w-]+
        )
        (?![\w-])[^\s]*$
    """,
    re.IGNORECASE | re.VERBOSE,
)

SUPPORTED_EMBED_PATTERNS = (YOUTUBE_URL_RE, FACEBOOK_URL_RE)

# URLs whose natural aspect ratio is portrait (9:16).
VERTICAL_URL_RE = re.compile(
    r"(?:facebook\.com/reel/|youtube\.com/shorts/)",
    re.IGNORECASE,
)

HORIZONTAL = "horizontal"
VERTICAL = "vertical"
VALID_ORIENTATIONS = (HORIZONTAL, VERTICAL)


def is_supported_embed_url(url: str) -> bool:
    """Return ``True`` if ``url`` is a supported YouTube or Facebook video URL."""
    return any(pattern.match(url) for pattern in SUPPORTED_EMBED_PATTERNS)


def infer_orientation(url: str) -> str:
    """Infer the display orientation for a supported embed URL.

    Reels and YouTube shorts are vertical (9:16); everything else is horizontal
    (16:9).
    """
    return VERTICAL if VERTICAL_URL_RE.search(url) else HORIZONTAL


def _field_values(block: str, name: str) -> list[str]:
    """Return the value of every ``<name>:`` line inside an embed block."""
    prefix = f"{name}:"
    values = []
    for raw_line in block.splitlines():
        line = raw_line.strip()
        if line.lower().startswith(prefix):
            values.append(line[len(prefix) :].strip())
    return values


def _validate_block(block: str) -> None:
    """Validate a single embed block body. Raises ``ValidationError``."""
    urls = _field_values(block, "url")
    if not urls:
        raise ValidationError("An embed block must contain a 'url:' line.")
    if len(urls) > 1:
        raise ValidationError(
            "An embed block must contain a single video. Use a separate embed block for each video.",
        )

    url = urls[0]
    if not url:
        raise ValidationError("An embed 'url:' line must contain a URL.")
    if not is_supported_embed_url(url):
        raise ValidationError(
            f"Unsupported embed URL: '{url}'. Only YouTube and Facebook video URLs are supported.",
        )

    orientations = _field_values(block, "orientation")
    if orientations and orientations[0].lower() not in VALID_ORIENTATIONS:
        raise ValidationError(
            f"Invalid embed orientation: '{orientations[0]}'. Must be one of: {', '.join(VALID_ORIENTATIONS)}.",
        )


def parse_embeds(content: str | None) -> list[dict]:
    """Parse every ``embed`` block in ``content`` into structured data.

    Returns a list of ``{"url", "orientation", "caption"}`` dicts, one per block.
    Orientation falls back to :func:`infer_orientation` when not explicitly set;
    caption is ``None`` when absent. This is the canonical reference for the block
    format; it does not validate (use :func:`validate_embeds` for that).
    """
    embeds = []
    for match in EMBED_BLOCK_RE.finditer(content or ""):
        block = match.group(1)
        urls = _field_values(block, "url")
        if not urls:
            continue
        url = urls[0]
        orientations = _field_values(block, "orientation")
        captions = _field_values(block, "caption")
        embeds.append(
            {
                "url": url,
                "orientation": orientations[0].lower() if orientations else infer_orientation(url),
                "caption": captions[0] if captions else None,
            },
        )
    return embeds


def validate_embeds(content: str | None) -> None:
    """Validate every ``embed`` block found in ``content``.

    Raises:
        ValidationError: If a block is missing its URL, has more than one URL,
            contains an unsupported URL, or declares an invalid orientation.
    """
    if not content:
        return
    for match in EMBED_BLOCK_RE.finditer(content):
        _validate_block(match.group(1))
