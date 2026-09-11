from apps.news.factories import NewsFactory
from apps.news.models import News
from main.tests.base_test import TestCase


class TestShowInPopupSingleton(TestCase):
    def _make(self, title, show_in_popup):
        return NewsFactory.create(
            title=title,
            content="x",
            published_date="2023-12-31",
            show_in_popup=show_in_popup,
        )

    def test_enabling_popup_clears_others(self):
        first = self._make("First", show_in_popup=True)
        second = self._make("Second", show_in_popup=True)

        first.refresh_from_db()
        second.refresh_from_db()
        assert first.show_in_popup is False
        assert second.show_in_popup is True
        assert News.objects.filter(show_in_popup=True).count() == 1

    def test_enabling_on_update_clears_others(self):
        first = self._make("First", show_in_popup=True)
        second = self._make("Second", show_in_popup=False)

        second.show_in_popup = True
        second.save()

        first.refresh_from_db()
        assert first.show_in_popup is False
        assert News.objects.filter(show_in_popup=True).count() == 1

    def test_saving_without_popup_leaves_others_untouched(self):
        active = self._make("Active", show_in_popup=True)
        self._make("Other", show_in_popup=False)

        active.refresh_from_db()
        assert active.show_in_popup is True
        assert News.objects.filter(show_in_popup=True).count() == 1
