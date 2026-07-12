"""
    author: ffpereira
    date: 2025-11-21
"""

from api.models import Country, Film
from tests.base_test_case import BaseTestCase


class GenresTest(BaseTestCase):

    def test_get_genres(self):
        rv = self.client.get('/api/genres')
        assert rv.status_code == 200
        data = rv.json

        assert len(data) == 2
        assert data[0]["id"] == "18"
        assert data[0]["name"] == "Drama"
        assert data[0]["film_count"] == 2
        assert data[1]["id"] == "36"
        assert data[1]["name"] == "History"
        assert data[1]["film_count"] == 1

        rv = self.client.get('/api/genres?in_cinemas=nope')
        assert rv.status_code == 400

    def test_get_genre(self):
        rv = self.client.get('/api/genre/18')
        assert rv.status_code == 200
        data = rv.json

        assert data["id"] == 18
        assert data["name"] == "Drama"

        rv = self.client.get('/api/genre/999')
        assert rv.status_code == 404
