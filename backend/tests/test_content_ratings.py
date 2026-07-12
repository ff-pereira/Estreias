"""
    author: ffpereira
    date: 2025-11-21
"""

from api.models import Country, Film
from tests.base_test_case import BaseTestCase


class ContentRatingsTest(BaseTestCase):

    def test_get_content_ratings(self):
        rv = self.client.get('/api/content_ratings')
        assert rv.status_code == 200
        data = rv.json

        assert len(data) == 3
        assert data[0]["id"] == "M/16"
        assert data[0]["film_count"] == 2
        assert data[1]["id"] == "M/12"
        assert data[2]["id"] == "M/6"

        rv = self.client.get('/api/content_ratings?title=Film&language=fr')
        assert rv.status_code == 200
        data = rv.json

        assert len(data) == 1
        assert data[0]["id"] == "M/12"
        assert data[0]["film_count"] == 1

        rv = self.client.get('/api/content_ratings?in_cinemas=nope')
        assert rv.status_code == 400

