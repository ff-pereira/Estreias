"""
    author: ffpereira
    date: 2025-11-21
"""

from datetime import datetime

from api.models import Country, Film
from tests.base_test_case import BaseTestCase

next_year_date = datetime.today().replace(year=datetime.now().year + 1).strftime("%Y-%m-%d")

class ReleasesTest(BaseTestCase):

    def test_get_releases(self):
        rv = self.client.get('/api/releases')
        assert rv.status_code == 200
        data = rv.json["data"]
        pagination = rv.json["pagination"]

        assert pagination["count"] == 4
        assert pagination["offset"] == 0
        assert pagination["limit"] == 60
        assert pagination["total"] == 4

        assert data[0]["country_id"] == "PT"
        assert data[0]["date"] == "2023-01-01"
        assert data[0]["film_id"] == "film-1"
        assert data[1]["country_id"] == "PT"
        assert data[1]["date"] == "2023-05-01"
        assert data[1]["film_id"] == "film-3"
        assert data[3]["country_id"] == "PT"
        assert data[3]["date"] == next_year_date
        assert data[3]["film_id"] == "film-4"

    def test_get_grouped_releases(self):
        rv = self.client.get('/api/grouped_releases')
        assert rv.status_code == 200
        data = rv.json["data"]
        pagination = rv.json["pagination"]

        assert pagination["count"] == 1
        assert pagination["offset"] == 3
        assert pagination["limit"] == 5
        assert pagination["total"] == 4

        assert data[0]["date"] == next_year_date
        assert len(data[0]["releases"]) == 1
        assert data[0]["releases"][0]["film_id"] == "film-4"
        assert data[0]["releases"][0]["distributor"] == "Nimas"

        two_years_from_now = datetime.today().replace(year=datetime.now().year + 2).strftime("%Y-%m-%d")
        rv = self.client.get(f'/api/grouped_releases?after={two_years_from_now}')
        assert rv.status_code == 200
        data = rv.json["data"]
        pagination = rv.json["pagination"]

        assert pagination["count"] == 0
        assert pagination["limit"] == 5
        assert len(data) == 0

        rv = self.client.get(f'/api/grouped_releases?before={two_years_from_now}&title_search=Future')
        assert rv.status_code == 200
        data = rv.json["data"]
        pagination = rv.json["pagination"]

        assert pagination["count"] == 1
        assert pagination["total"] == 1
        assert data[0]["date"] == next_year_date
        assert len(data[0]["releases"]) == 1
        assert data[0]["releases"][0]["film_id"] == "film-4"
        assert data[0]["releases"][0]["distributor"] == "Nimas"

        rv = self.client.get(f'/api/grouped_releases?cinemas=cinema-2')
        assert rv.status_code == 200
        data = rv.json["data"]
        pagination = rv.json["pagination"]

        assert pagination["count"] == 1
        assert pagination["total"] == 1
        assert data[0]["date"] == "2023-01-01"
        assert len(data[0]["releases"]) == 1
        assert data[0]["releases"][0]["film_id"] == "film-1"
        assert data[0]["releases"][0]["title"] == "Full Film"

        rv = self.client.get(f'/api/grouped_releases?offset=1&limit=1')
        assert rv.status_code == 200
        data = rv.json["data"]
        pagination = rv.json["pagination"]

        assert pagination["count"] == 1
        assert pagination["limit"] == 1
        assert pagination["offset"] == 1
        assert pagination["total"] == 4
        assert len(data[0]["releases"]) == 1
        assert data[0]["releases"][0]["film_id"] == "film-3"
        assert len(data[0]["releases"][0]["directors"]) == 1
        assert len(data[0]["releases"][0]["genres"]) == 0

        rv = self.client.get(f'/api/grouped_releases?after=wrong')
        assert rv.status_code == 400

        rv = self.client.get(f'/api/grouped_releases?after=2026-04-01&before=2025-04-01')
        assert rv.status_code == 400
