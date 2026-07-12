"""
    author: ffpereira
    date: 2025-11-21
"""

from datetime import datetime

from api.models import Country, Film
from tests.base_test_case import BaseTestCase


class CinemasTest(BaseTestCase):

    def test_get_cinemas(self):
        rv = self.client.get('/api/cinemas')
        assert rv.status_code == 200
        data = rv.json

        assert len(data) == 2
        assert data[0]["group"] is None
        assert data[0]["id"] == "cinema-1"
        assert data[1]["name"] == "Cinema 2"

        rv = self.client.get('/api/cinemas?name=Cinema&cities=Guarda')
        assert rv.status_code == 200
        data = rv.json

        assert len(data) == 1
        assert data[0]["group"] is None
        assert data[0]["id"] == "cinema-1"
        assert data[0]["name"] == "Cinema 1"

        rv = self.client.get('/api/cinemas?groups=UCI,Cinemax&film_id=film-1')
        assert rv.status_code == 200
        data = rv.json

        assert len(data) == 1
        assert data[0]["group"] == "UCI"
        assert data[0]["id"] == "cinema-2"
        assert data[0]["name"] == "Cinema 2"

    def test_get_cinema(self):
        rv = self.client.get('/api/cinema/cinema-1')
        assert rv.status_code == 200
        data = rv.json

        assert data["group"] is None
        assert data["id"] == "cinema-1"
        assert data["name"] == "Cinema 1"

        rv = self.client.get('/api/cinema/cinema-2')
        assert rv.status_code == 200
        data = rv.json

        assert data["id"] == "cinema-2"
        assert data["address_region"] == "Porto"
        assert data["group"] == "UCI"
        assert data["latitude"] is None
        assert data["longitude"] is None
        assert data["name"] == "Cinema 2"
        assert data["telephone"] == "16996"

        rv = self.client.get('/api/cinema/123')
        assert rv.status_code == 404

    def test_get_cinema_now_showing(self):
        rv = self.client.get('/api/cinema/cinema-2/now_showing')
        assert rv.status_code == 200
        data = rv.json

        print(data)

        assert len(data) == 1
        assert data[0]["id"] == "film-1"
        assert data[0]["title"] == "Full Film"
        assert data[0]["release_year"] == 2023
        assert data[0]["last_seen"] == datetime.today().strftime("%Y-%m-%d")

    def test_cities(self):
        rv = self.client.get('/api/cities')
        assert rv.status_code == 200
        data = rv.json["data"]

        assert len(data) == 2
        assert data[0]["name"] == "Guarda"
        assert data[1]["id"] == "Porto"
        assert data[1]["name"] == "Porto"

    def test_portuguese_regions(self):
        rv = self.client.get('/api/portugal_regions')
        assert rv.status_code == 200
        data = rv.json["data"]

        assert len(data) == 2
        assert data[0]["id"] == "Guarda"
        assert data[0]["name"] == "Guarda"
        assert data[0]["count"] == 1
        assert data[1]["id"] == "Porto"
        assert data[1]["name"] == "Porto"
        assert data[1]["count"] == 1

        rv = self.client.get('/api/portugal_regions?cities=Porto&groups=UCI&film_id=film-1')
        assert rv.status_code == 200
        data = rv.json["data"]

        assert len(data) == 1
        assert data[0]["id"] == "Porto"
        assert data[0]["name"] == "Porto"
        assert data[0]["count"] == 1

    def test_cinema_groups(self):
        rv = self.client.get('/api/cinema_groups')
        assert rv.status_code == 200
        data = rv.json["data"]

        assert len(data) == 1
        assert data[0]["id"] == "UCI"
        assert data[0]["name"] == "UCI"