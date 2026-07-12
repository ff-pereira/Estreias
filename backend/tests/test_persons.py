"""
    author: ffpereira
    date: 2025-11-21
"""

from api.models import Country, Film
from tests.base_test_case import BaseTestCase


class PersonsTest(BaseTestCase):

    def test_get_persons(self):
        rv = self.client.get('/api/persons')
        assert rv.status_code == 200
        data = rv.json["data"]
        pagination = rv.json["pagination"]

        assert pagination["count"] == 4
        assert pagination["offset"] == 0
        assert pagination["limit"] == 60
        assert pagination["total"] == 4

        assert data[0]["id"] == 4
        assert data[0]["imdb_id"] is None
        assert data[0]["name"] == "Director Two"
        assert len(data[0]["cast_roles"]) == 0
        assert len(data[0]["crew_roles"]) == 2
        assert data[1]["id"] == 1
        assert data[1]["name"] == "Director"
        assert data[2]["id"] == 3
        assert data[2]["name"] == "Actor Two"
        assert data[2]["birthday"] is None
        assert len(data[2]["cast_roles"]) == 3
        assert len(data[2]["crew_roles"]) == 0

        # Max limit is 200
        rv = self.client.get('/api/persons?limit=300')
        assert rv.status_code == 200
        pagination = rv.json["pagination"]
        assert pagination["count"] == 4
        assert pagination["offset"] == 0
        assert pagination["limit"] == 200

        rv = self.client.get('/api/persons?offset=-12')
        assert rv.status_code == 400



    def test_get_person(self):
        rv = self.client.get('/api/person/2')
        assert rv.status_code == 200
        data = rv.json

        assert data["id"] == 2
        assert data["imdb_id"] is None
        assert data["name"] == "Actor One"
        assert len(data["cast_roles"]) == 2
        assert len(data["crew_roles"]) == 0

        rv = self.client.get('/api/person/123')
        assert rv.status_code == 404

        rv = self.client.get('/api/person/wrong')
        assert rv.status_code == 400

    def test_get_person_roles(self):
        rv = self.client.get('/api/person/roles/1')
        assert rv.status_code == 200
        data = rv.json

        assert data["Actor"] == 0
        assert data["Director"] == 2
        assert data["Camera"] == 1
        assert data["Sound"] == 1
        assert data["Writer"] == 1

        rv = self.client.get('/api/person/roles/2')
        assert rv.status_code == 200
        data = rv.json

        assert data["Actor"] == 2
        assert data["Director"] == 0
        assert data["Camera"] == 0
        assert data["Sound"] == 0
        assert data["Writer"] == 0

        rv = self.client.get('/api/person/roles/123')
        assert rv.status_code == 404

        rv = self.client.get('/api/person/roles/wrong')
        assert rv.status_code == 400

    def test_get_cast_counts(self):
        rv = self.client.get('/api/cast')
        assert rv.status_code == 200
        data = rv.json["data"]
        pagination = rv.json["pagination"]

        assert pagination["count"] == 2
        assert pagination["offset"] == 0
        assert pagination["limit"] == 60
        assert pagination["total"] == 2

        assert data[0]["id"] == 3
        assert data[0]["name"] == "Actor Two"
        assert data[0]["count"] == 3
        assert data[1]["id"] == 2
        assert data[1]["name"] == "Actor One"
        assert data[1]["count"] == 2

        rv = self.client.get('/api/cast?gender=2&name=Actor')
        assert rv.status_code == 200
        data = rv.json["data"]
        pagination = rv.json["pagination"]

        assert pagination["count"] == 1
        assert pagination["offset"] == 0
        assert pagination["limit"] == 60
        assert pagination["total"] == 1

        assert data[0]["id"] == 2
        assert data[0]["name"] == "Actor One"
        assert data[0]["count"] == 2

        rv = self.client.get('/api/cast?gender=wrong')
        assert rv.status_code == 400

        rv = self.client.get('/api/cast?gender=16')
        assert rv.status_code == 400

        print(data)

    def test_get_crew_counts(self):
        rv = self.client.get('/api/crew')
        assert rv.status_code == 200
        data = rv.json["data"]
        pagination = rv.json["pagination"]

        assert pagination["count"] == 2
        assert pagination["offset"] == 0
        assert pagination["limit"] == 60
        assert pagination["total"] == 2

        assert data[0]["id"] == 1
        assert data[0]["name"] == "Director"
        assert data[0]["count"] == 5
        assert data[1]["id"] == 4
        assert data[1]["name"] == "Director Two"
        assert data[1]["count"] == 2

        rv = self.client.get('/api/crew?gender=1&name=Director&role=director')
        assert rv.status_code == 200
        data = rv.json["data"]
        pagination = rv.json["pagination"]

        assert pagination["count"] == 2
        assert pagination["offset"] == 0
        assert pagination["limit"] == 60
        assert pagination["total"] == 2

        assert data[0]["id"] == 1
        assert data[0]["name"] == "Director"
        assert data[0]["count"] == 2

        rv = self.client.get('/api/crew?gender=wrong')
        assert rv.status_code == 400

        rv = self.client.get('/api/crew?gender=16')
        assert rv.status_code == 400

        rv = self.client.get('/api/crew?role=cleaner')
        assert rv.status_code == 400
