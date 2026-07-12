"""
    author: ffpereira
    date: 2025-11-21
"""
from datetime import datetime

from api.models import Country, Film
from tests.base_test_case import BaseTestCase


class StatsTest(BaseTestCase):

    def test_get_stats(self):
        rv = self.client.get('/api/stats')
        assert rv.status_code == 200
        data = rv.json

        assert len(data["grouped"]["films_by_content_rating"]) == 3
        assert len(data["grouped"]["films_by_country"]) == data["total"]["countries"] == 2
        assert len(data["grouped"]["films_by_distributor"]) == data["total"]["distributors"] == 3
        assert len(data["grouped"]["films_by_genre"]) == data["total"]["genres"] == 2
        assert len(data["grouped"]["films_by_language"]) == data["total"]["languages"] ==2
        assert data["top"]["popular"][0]["id"] == "film-1"
        assert data["top_crew_by_gender"]["director"]["1"][0]["name"] == "Director"
        assert data["top_actors_by_gender"]["2"][0]["name"] == "Actor One"
        assert data["total"]["films"] == 4
        assert data["total"]["released"] == 3
        assert data["total"]["upcoming"] == 1
        assert data["total"]["female_directed"] == 0
        assert data["total"]["actors"] == 2
        assert data["total"]["directors"] == 2
        assert data["total"]["composers"] == 1
        assert data["total"]["writers"] == 2
        assert data["total"]["percentage_animation_films"] == 0.0
        assert data["total"]["percentage_actors_with_multiple_films"] == 100.0

        rv = self.client.get('/api/stats?language=fr&distributor=CinemasNOS')
        assert rv.status_code == 200
        data = rv.json

        assert data["total"]["languages"] == 1
        assert data["total"]["films"] == 1
        assert data["total"]["directors"] == 1
        assert data["total"]["released"] == 1
        assert data["total"]["actors"] == 2

        rv = self.client.get('/api/stats?release_year=2023&runtime=<100')
        assert rv.status_code == 200
        data = rv.json

        assert data["total"]["distributors"] == 1
        assert data["total"]["films"] == 1
        assert data["total"]["languages"] == 1
        assert data["total"]["distributors"] == 1
        assert data["total"]["directors_with_one_film"] == 1
        assert data["total"]["documentary_films"] == 0

        rv = self.client.get('/api/stats?genre=18&country=US&cinema=cinema-2&runtime=>1')
        assert rv.status_code == 200
        data = rv.json

        assert data["total"]["films"] == 1
        assert data["total"]["genres"] == 2
        assert data["total"]["with_portugal"] == 1
        assert data["total"]["writers"] == 1
        assert data["total"]["upcoming"] == 0
        assert data["total"]["released"] == 1

        next_year = datetime.today().year + 1
        rv = self.client.get(f'/api/stats?pt_release_year={next_year}&runtime=0-200')
        assert rv.status_code == 200
        data = rv.json

        assert data["total"]["films"] == 1
        assert data["total"]["upcoming"] == 1
        assert data["total"]["released"] == 0
        assert data["total"]["directors"] == 1
        assert len(data["grouped"]["films_by_content_rating"]) == 1
        assert len(data["grouped"]["films_by_country"]) == 2

        rv = self.client.get('/api/stats?month=5&content_rating=M-12')
        assert rv.status_code == 200
        data = rv.json

        assert data["total"]["films"] == 1
        assert data["total"]["released"] == 1
        assert data["total"]["upcoming"] == 0
        assert data["total"]["voice_performances"] == 0

        rv = self.client.get('/api/stats?release_year=wrong')
        assert rv.status_code == 400

        rv = self.client.get('/api/stats?pt_release_year=wrong')
        assert rv.status_code == 400

        rv = self.client.get('/api/stats?runtime=wrong')
        assert rv.status_code == 400

        rv = self.client.get('/api/stats?genre=wrong')
        assert rv.status_code == 400

        rv = self.client.get('/api/stats?content_rating=wrong')
        assert rv.status_code == 400

        rv = self.client.get('/api/stats?month=14')
        assert rv.status_code == 400

        rv = self.client.get('/api/stats?month=wrong')
        assert rv.status_code == 400
