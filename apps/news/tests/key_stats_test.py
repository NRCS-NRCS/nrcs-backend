from django.forms.models import inlineformset_factory

from apps.news.admin import KeyStatInlineFormSet
from apps.news.factories import KeyStatFactory, NewsFactory
from apps.news.models import KeyStat, News
from apps.strategic.factories import UserFactory
from main.tests.base_test import TestCase


class TestNewsKeyStatQuery(TestCase):
    QUERY = """
      query news {
        news {
            results {
                id
                keyStats {
                    order
                    title
                    stat
                    featured
                }
            }
        }
      }
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = UserFactory.create(username="nrcs-keystat-test")

    def test_key_stats_returned_ordered(self):
        news = NewsFactory.create(title="With stats", content="x", published_date="2023-12-31")
        # Created out of order to confirm the response is ordered by `order`.
        KeyStatFactory.create(news=news, order=2, title="Second", stat=20, featured=False)
        KeyStatFactory.create(news=news, order=1, title="First", stat=10, featured=True)

        content = self.query_check(self.QUERY)
        assert content["data"]["news"]["results"] == [
            {
                "id": self.gID(news.id),
                "keyStats": [
                    {"order": 1, "title": "First", "stat": 10, "featured": True},
                    {"order": 2, "title": "Second", "stat": 20, "featured": False},
                ],
            },
        ], content


class TestKeyStatFeaturedLimit(TestCase):
    FormSet = inlineformset_factory(
        News,
        KeyStat,
        formset=KeyStatInlineFormSet,
        fields=["order", "title", "stat", "featured"],
        extra=0,
        can_delete=True,
    )

    def _build(self, featured_flags):
        n = len(featured_flags)
        data = {
            "key_stats-TOTAL_FORMS": str(n),
            "key_stats-INITIAL_FORMS": "0",
            "key_stats-MIN_NUM_FORMS": "0",
            "key_stats-MAX_NUM_FORMS": "1000",
        }
        for i, featured in enumerate(featured_flags):
            data[f"key_stats-{i}-order"] = str(i + 1)
            data[f"key_stats-{i}-title"] = f"Stat {i}"
            data[f"key_stats-{i}-stat"] = str(100 + i)
            if featured:
                data[f"key_stats-{i}-featured"] = "on"
        formset = self.FormSet(data=data, instance=News())
        formset.is_valid()
        return formset.non_form_errors()

    def test_four_featured_allowed(self):
        assert self._build([True, True, True, True]) == []

    def test_five_featured_rejected(self):
        errors = self._build([True, True, True, True, True])
        assert errors
        assert "at most 4 featured" in errors[0]

    def test_many_stats_few_featured_allowed(self):
        assert self._build([True, False, True, False, False, False]) == []
