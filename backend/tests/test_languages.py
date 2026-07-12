"""
    author: ffpereira
    date: 2025-11-21
"""

from api.models import Country, Film
from tests.base_test_case import BaseTestCase


class LanguagesTest(BaseTestCase):

    def test_get_languages(self):
        rv = self.client.get('/api/languages')
        assert rv.status_code == 200
        data = rv.json

        assert len(data) == 2
        assert data[0]["id"] == "en"
        assert data[1]["id"] == "fr"

        rv = self.client.get('/api/languages?in_cinemas=nope')
        assert rv.status_code == 400

    def test_get_language(self):
        rv = self.client.get('/api/language/en')
        assert rv.status_code == 200
        data = rv.json

        assert data["id"] == "en"

        rv = self.client.get('/api/language/xx')
        assert rv.status_code == 404