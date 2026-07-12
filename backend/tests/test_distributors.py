"""
    author: ffpereira
    date: 2025-11-21
"""

from api.models import Country, Film
from tests.base_test_case import BaseTestCase


class DistributorsTest(BaseTestCase):

    def test_get_distributors(self):
        rv = self.client.get('/api/distributors')
        assert rv.status_code == 200
        data = rv.json

        assert len(data) == 3
        assert data[0]["id"] == "Cinemundo"
        assert data[0]["film_count"] == 2
        assert data[1]["id"] == "CinemasNOS"
        assert data[2]["id"] == "Nimas"

        rv = self.client.get('/api/distributors?in_cinemas=false&countries=US,PT')
        assert rv.status_code == 200
        data = rv.json

        assert len(data) == 1
        assert data[0]["id"] == "CinemasNOS"
        assert data[0]["film_count"] == 1

        rv = self.client.get('/api/distributors?in_cinemas=nope')
        assert rv.status_code == 400

    def test_get_distributor(self):
        rv = self.client.get('/api/distributor/Cinemundo')
        assert rv.status_code == 200
        data = rv.json

        assert data["id"] == "Cinemundo"
        assert data["name"] == "Cinemundo"

        rv = self.client.get('/api/distributor/NeverlandProductions')
        assert rv.status_code == 404

