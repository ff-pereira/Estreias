"""
    author: ffpereira
    date: 2025-11-21
"""

from api.models import Country, Film
from tests.base_test_case import BaseTestCase


class CountriesTest(BaseTestCase):

    def test_get_countries(self):
        rv = self.client.get('/api/countries')
        assert rv.status_code == 200
        data = rv.json

        assert len(data) == 2

        assert data[0]["id"] == "PT"
        assert data[0]["name"] == "Portugal"
        assert data[1]["id"] == "US"
        assert data[1]["name"] == "United States"

        rv = self.client.get('/api/countries?in_cinemas=1&genres=18&distributors=Cinemundo&content_ratings=M-16')
        assert rv.status_code == 200
        data = rv.json

        assert data[0]["id"] == "PT"
        assert data[0]["name"] == "Portugal"
        assert data[1]["id"] == "US"
        assert data[1]["name"] == "United States"

        print(data)

    def test_get_country(self):
        rv = self.client.get('/api/country/PT')
        assert rv.status_code == 200
        data = rv.json

        assert data["id"] == "PT"
        assert data["name"] == "Portugal"

        rv = self.client.get('/api/country/XX')
        assert rv.status_code == 404