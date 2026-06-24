import pytest
from django.core.exceptions import ValidationError

from utils.embed import (
    HORIZONTAL,
    VERTICAL,
    infer_orientation,
    is_supported_embed_url,
    parse_embeds,
    validate_embeds,
)


class TestSupportedEmbedUrl:
    @pytest.mark.parametrize(
        "url",
        [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtube.com/watch?v=dQw4w9WgXcQ&t=10s",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://www.youtube.com/embed/dQw4w9WgXcQ",
            "https://www.youtube.com/shorts/dQw4w9WgXcQ",
            "https://m.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://www.facebook.com/watch/?v=123456789",
            "https://www.facebook.com/reel/123456789",
            "https://www.facebook.com/reel/1527219472411989",
            "https://www.facebook.com/somepage/videos/123456789",
            "https://www.facebook.com/somepage/videos/some-slug/123456789/",
            "https://web.facebook.com/video.php?v=123456789",
            "https://fb.watch/abcd1234/",
        ],
    )
    def test_supported_urls(self, url):
        assert is_supported_embed_url(url) is True

    @pytest.mark.parametrize(
        "url",
        [
            "https://facebook/reel/asjdna",  # missing .com
            "https://youtuvbe.com/jkansdkjnas",  # typo domain
            "https://vimeo.com/123456789",  # unsupported provider
            "https://example.com/watch?v=123",
            "https://www.youtube.com/",  # no video id
            "not-a-url",
        ],
    )
    def test_unsupported_urls(self, url):
        assert is_supported_embed_url(url) is False


class TestValidateEmbeds:
    def test_empty_content_is_valid(self):
        validate_embeds(None)
        validate_embeds("")
        validate_embeds("Just some **markdown** with no embeds.")

    def test_valid_single_embed(self):
        content = (
            "Intro text\n\n"
            "```embed\n"
            "url: https://www.youtube.com/watch?v=dQw4w9WgXcQ\n"
            "orientation: horizontal\n"
            "caption: A great video\n"
            "```\n"
        )
        validate_embeds(content)

    def test_multiple_independent_blocks(self):
        content = (
            "```embed\n"
            "url: https://youtu.be/dQw4w9WgXcQ\n"
            "caption: First\n"
            "```\n\n"
            "Some text in between.\n\n"
            "```embed\n"
            "url: https://www.facebook.com/reel/123456789\n"
            "orientation: vertical\n"
            "caption: Second\n"
            "```"
        )
        validate_embeds(content)

    def test_unsupported_url_rejected(self):
        content = "```embed\nurl: https://vimeo.com/123456789\ncaption: nope\n```"
        with pytest.raises(ValidationError):
            validate_embeds(content)

    def test_bad_url_in_one_of_many_blocks_rejected(self):
        content = "```embed\nurl: https://youtu.be/dQw4w9WgXcQ\n```\n\n```embed\nurl: https://facebook/reel/asjdna\n```"
        with pytest.raises(ValidationError):
            validate_embeds(content)

    def test_multiple_urls_in_one_block_rejected(self):
        content = "```embed\nurl: https://youtu.be/dQw4w9WgXcQ\nurl: https://www.facebook.com/reel/123456789\n```"
        with pytest.raises(ValidationError):
            validate_embeds(content)

    def test_missing_url_line_rejected(self):
        content = "```embed\ncaption: only a caption\n```"
        with pytest.raises(ValidationError):
            validate_embeds(content)

    def test_valid_orientation_accepted(self):
        for orientation in (HORIZONTAL, VERTICAL):
            content = f"```embed\nurl: https://www.facebook.com/reel/1527219472411989\norientation: {orientation}\n```"
            validate_embeds(content)

    def test_invalid_orientation_rejected(self):
        content = "```embed\nurl: https://youtu.be/dQw4w9WgXcQ\norientation: diagonal\n```"
        with pytest.raises(ValidationError):
            validate_embeds(content)


class TestParseEmbeds:
    def test_parses_each_block_independently(self):
        content = (
            "```embed\n"
            "url: https://www.facebook.com/reel/1527219472411989\n"
            "caption: A reel\n"
            "```\n\n"
            "```embed\n"
            "url: https://www.youtube.com/watch?v=dQw4w9WgXcQ\n"
            "orientation: vertical\n"
            "```"
        )
        assert parse_embeds(content) == [
            {
                "url": "https://www.facebook.com/reel/1527219472411989",
                "orientation": VERTICAL,  # inferred (reel)
                "caption": "A reel",
            },
            {
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "orientation": VERTICAL,  # explicit override
                "caption": None,
            },
        ]

    def test_no_blocks(self):
        assert parse_embeds("just text") == []
        assert parse_embeds(None) == []


class TestInferOrientation:
    @pytest.mark.parametrize(
        "url",
        [
            "https://www.facebook.com/reel/1527219472411989",
            "https://www.youtube.com/shorts/dQw4w9WgXcQ",
        ],
    )
    def test_vertical(self, url):
        assert infer_orientation(url) == VERTICAL

    @pytest.mark.parametrize(
        "url",
        [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://www.facebook.com/somepage/videos/123456789",
        ],
    )
    def test_horizontal(self, url):
        assert infer_orientation(url) == HORIZONTAL
