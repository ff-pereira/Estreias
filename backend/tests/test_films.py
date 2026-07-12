"""
    author: ffpereira
    date: 2025-11-21
"""

from api.models import Country, Film
from tests.base_test_case import BaseTestCase


class FilmsTest(BaseTestCase):

    def test_get_films(self):
        rv = self.client.get('/api/films')
        assert rv.status_code == 200
        data = rv.json["data"]
        pagination = rv.json["pagination"]

        assert pagination["count"] == 3
        assert pagination["limit"] == 60
        assert pagination["offset"] == 0
        assert pagination["total"] == 3

        assert len(data) == 3
        assert data[0]["id"] == "film-1"
        assert data[0]["title"] == "Full Film"
        assert data[0]["budget"] is None
        assert data[1]["id"] == "film-3"
        assert data[1]["title"] == "International Film"
        assert data[1]["pt_release_date"] == "2023-05-01"
        assert data[1]["distributor"] == "CinemasNOS"
        assert data[1]["upcoming"] == False
        assert data[2]["title"] == "Future Film"
        assert data[2]["content_rating"] == "M/6"
        assert data[2]["id"] == "film-4"
        assert data[2]["in_cinemas"] == False

        rv = self.client.get('/api/films?sort=runtime&release_year=2023&sort_dir=desc')
        assert rv.status_code == 200
        data = rv.json["data"]
        pagination = rv.json["pagination"]

        assert pagination["count"] == 2
        assert pagination["offset"] == 0
        assert pagination["total"] == 2

        assert len(data) == 2
        assert data[0]["id"] == "film-1"
        assert data[0]["release_date"] == "2023-01-01"
        assert data[0]["runtime"] == 101
        assert data[1]["id"] == "film-3"
        assert data[1]["release_date"] == "2023-05-01"
        assert data[1]["runtime"] == 88

        rv = self.client.get('/api/films?sort=runtime&sort_dir=desc&upcoming=true&runtime=131')
        assert rv.status_code == 200
        data = rv.json["data"]
        pagination = rv.json["pagination"]

        assert pagination["count"] == 1
        assert pagination["offset"] == 0
        assert pagination["total"] == 1

        assert len(data) == 1
        assert data[0]["title"] == "Future Film"
        assert data[0]["revenue"] is None
        assert data[0]["revenue"] is None
        assert data[0]["id"] == "film-4"
        assert data[0]["upcoming"] == True

        rv = self.client.get('/api/films?cinemas=cinema-1,cinema-2&pt_release_date=2023-01-01')
        assert rv.status_code == 200
        data = rv.json["data"]
        pagination = rv.json["pagination"]

        assert pagination["count"] == 1
        assert pagination["offset"] == 0
        assert pagination["total"] == 1

        assert data[0]["id"] == "film-1"
        assert data[0]["release_date"] == "2023-01-01"
        assert data[0]["runtime"] == 101

        rv = self.client.get('/api/films?sort=runtime&sort_dir=wrong')
        assert rv.status_code == 400

        rv = self.client.get('/api/films?sort=wrong')
        assert rv.status_code == 400

        rv = self.client.get('/api/films?pt_release_date=wrong')
        assert rv.status_code == 400

        rv = self.client.get('/api/films?release_year=wrong')
        assert rv.status_code == 400

    def test_get_film(self):
        rv = self.client.get('/api/film/film-1')
        assert rv.status_code == 200
        data = rv.json

        assert data["id"] == "film-1"
        assert data["title"] == "Full Film"
        assert data["distributor"] == "Cinemundo"
        assert len(data["cast"]) == 2
        assert len(data["crew"]) == 4
        assert len(data["screenings"]) == 1
        assert data["countries"][0]["id"] == "PT"
        assert data["countries"][1]["id"] == "US"
        assert data["genres"][0]["name"] == "Drama"
        assert data["genres"][1]["name"] == "History"
        assert data["upcoming"] == False
        assert data["tmdb_id"] is None

        rv = self.client.get('/api/film/film-2')
        assert rv.status_code == 200
        data = rv.json

        assert data["id"] == "film-2"
        assert data["title"] == "Minimal Film"
        assert data["budget"] is None
        assert len(data["cast"]) == 0
        assert len(data["crew"]) == 0
        assert len(data["screenings"]) == 0
