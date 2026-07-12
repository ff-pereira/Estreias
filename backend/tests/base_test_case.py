"""
    author: ffpereira
    date: 2025-11-21
"""

import unittest
from datetime import datetime

from config import Config
from api.app import create_app, db
from api.models import Film, Country, Language, Genre, Cinema, Person, Cast, Crew, Release, Screening

class TestConfig(Config):
    TESTING = True
    ALCHEMICAL_DATABASE_URL = 'sqlite://'


class BaseTestCase(unittest.TestCase):
    config = TestConfig

    def setUp(self):
        self.app = create_app(self.config)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.create_test_data()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.close()
        db.drop_all()
        self.app_context.pop()

    """
    def create_test_data(self):
        # Countries
        countries_data = [
            {"id": "pt", "name": "Portugal"},
            {"id": "us", "name": "United States"},
            {"id": "uk", "name": "United Kingdom"},
        ]
        countries = [Country(**data) for data in countries_data]
        db.session.add_all(countries)

        languages_data = [
            {"id": "en", "name": "English", "english_name": "English"},
            {"id": "pl", "name": "Polski", "english_name": "Polish"},
            {"id": "no", "name": "Norsk", "english_name": "Norwegian"},
        ]
        languages = [Language(**data) for data in languages_data]
        db.session.add_all(languages)

        genres_data = [
            {"id": 12, "name": "Adventure"},
            {"id": 18, "name": "Drama"},
            {"id": 16, "name": "Animation"},
            {"id": 14, "name": "Fantasy"},
            {"id": 878, "name": "Science Fiction"},
            {"id": 10749, "name": "Romance"},
            {"id": 36, "name": "History"},
        ]
        genres = [Genre(**data) for data in genres_data]
        db.session.add_all(genres)

        cinemas_data = [
            {"id": "cinemas-nos-colombo-lisboa-27", "name": "Cinemas NOS Colombo - Lisboa", "group": "Cinemas NOS", "country_id": "PT",
             "latitude": 38.7545166, "longitude": -9.1874781, "street_address": "Av. Lusíada", "postal_code": "1500-392", "address_region": "Lisboa",
             "address_country": "Portugal", "address_locality": None, "telephone": "16996"},
            {"id": "uci-cinemas-el-corte-ingles-lisboa-61", "name": "UCI Cinemas El Corte Inglés - Lisboa",
             "group": "UCI Cinemas", "country_id": "PT", "latitude": 38.733841, "longitude": -9.153821,
             "street_address": "Avenida António Augusto Aguiar, 31", "postal_code": "1069-413",
             "address_region": "Lisboa", "address_country": "Portugal", "address_locality": None, "telephone": None}
        ]
        cinemas = [Cinema(**data) for data in cinemas_data]
        db.session.add_all(cinemas)

        persons_data = [
            {"id": 578, "name": "Ridley Scott", "original_name": "Ridley Scott", "gender": 1, "imdb_id": "nm0000631", "popularity": 5.3,
             "birthday": datetime(1937, 11, 30), "deathday": None, "pob": "South Shields, County Durham, England, UK",
             "known_for_department": "Directing", "biography": "Sir Ridley Scott is an English film director and producer."},
            {"id": 73421, "name": "Joaquin Phoenix", "original_name": "Joaquin Phoenix", "gender": 1, "imdb_id": "nm0001618", "popularity": 6.7,
             "birthday": datetime(1974, 10, 28), "date}_of_death": None, "pob": "San Juan, Puerto Rico", "known_for_department": "Acting",
             "biography": "Joaquin Phoenix is an American actor and producer."},
            {"id": 556356, "name": "Vanessa Kirby", "original_name": "Vanessa Kirby", "gender": 2, "imdb_id": "nm3948952", "popularity": 4.2,
             "birthday": datetime(1987, 4, 18), "deathday": None, "pob": "Wimbledon, London, England, UK", "known_for_department": "Acting",
             "biography": "Vanessa Kirby is an English actress."},
            {"id": 21527, "name":"David Scarpa", "original_name": "David Scarpa", "gender": 1, "imdb_id": "nm0769227", "popularity": 2.1,
             "birthday": None, "deathday": None, "pob": "Fort Campbell, Kentucky, USA", "known_for_department": "Writing", "biography": None},
            {"id": 139904, "name": "Martin Phipps", "original_name": "Martin Phipps", "gender": 1, "imdb_id": "nm0686445", "popularity": 1.8,
             "birthday": None, "deathday": None, "pob": "United Kingdom", "known_for_department": "Sound", "biography": None},
            {"id": 120, "name": "Dariusz Wolski", "original_name": "Dariusz Wolski", "gender": 1, "imdb_id": "nm0931321", "popularity": 3.5,
             "birthday": datetime(1956, 5, 7), "deathday": None, "pob": "Warsaw, Poland", "known_for_department": "Camera",
             "biography": "Dariusz Wolski is a Polish cinematographer."},
        ]
        persons = [Person(**data) for data in persons_data]
        db.session.add_all(persons)

        cast_data = [
            {"person_id": 73421, "film_id": "napoleon-753342", "character": "Napoleon Bonaparte", "order": 0},
            {"person_id": 556356, "film_id": "napoleon-753342", "character": "Josephine Bonaparte", "order": 1},
        ]
        cast = [Cast(**data) for data in cast_data]
        db.session.add_all(cast)

        crew_data = [
            {"person_id": 578, "film_id": "napoleon-753342", "role": "Director"},
            {"person_id": 21527, "film_id": "napoleon-753342", "role": "Writer"},
            {"person_id": 139904, "film_id": "napoleon-753342", "role": "Sound"},
            {"person_id": 120, "film_id": "napoleon-753342", "role": "Camera"},
        ]
        crew = [Crew(**data) for data in crew_data]
        db.session.add_all(crew)

        film_data = [
            {
                "id": "napoleon-753342", "imdb_id": "tt13287846", "tmdb_id": 753342,
                "title": "Napoleon", "original_title": "Napoleon", "portuguese_title": "Napoleão",
                "release_year": 2023, "release_date": "2023-11-22", "runtime": 158,
                "content_rating": "M/16",
                "description": "An epic that details the rise and fall of French Emperor Napoleon Bonaparte and his relentless journey to power.",
                "portuguese_description": "Um épico que retrata a ascensão e queda do imperador francês Napoleão Bonaparte e a sua implacável jornada pelo poder.",
                "distributor": "Cinemundo", "original_language": "en",
                "tagline": "He came from nothing. He conquered everything.",
                "budget": 200000000, "revenue": 221000000,
                "in_cinemas": False
            }
        ]
        film = Film(**film_data[0])
        film.countries = [countries[1], countries[2]]
        film.languages = [languages[0]]
        film.genres = [genres[0], genres[1], genres[3]]
        film.cinemas = [cinemas[0], cinemas[1]]
        film.cast = [cast[0], cast[1]]
        film.crew = [crew[0], crew[1], crew[2], crew[3]]
        db.session.add(film)

        db.session.commit()
    """

    def create_test_data(self):
        pt = Country(id="PT", name="Portugal")
        us = Country(id="US", name="United States")

        en = Language(id="en", name="English", english_name="English")
        fr = Language(id="fr", name="Français", english_name="French")

        drama = Genre(id=18, name="Drama")
        history = Genre(id=36, name="History")
        scifi = Genre(id=878, name="Sci-Fi")

        cinema1 = Cinema(id="cinema-1", name="Cinema 1", address_region="Guarda", country_id="PT")
        cinema2 = Cinema(id="cinema-2", name="Cinema 2", group="UCI", telephone="16996", address_region="Porto", country_id="PT")

        director1 = Person(id=1, name="Director", birthday=datetime(1970, 1, 1), gender=1)
        director2 = Person(id=4, name="Director Two", birthday=datetime(1942, 1, 1), gender=1)
        actor1 = Person(id=2, name="Actor One", birthday=datetime(1980, 1, 1), gender=2)
        actor2 = Person(id=3, name="Actor Two", gender=3)

        db.session.add_all([pt, us, en, fr, drama, history, scifi, cinema1, cinema2, director1, director2, actor1, actor2])

        # FILM 1: FULL DATA (your "golden film")
        film1 = Film(
            id="film-1",
            title="Full Film",
            original_title="Full Film",
            release_date=datetime(2023, 1, 1),
            original_language="en",
            in_cinemas=True,
            release_year=2023,
            content_rating="M/16",
            distributor="Cinemundo",
            runtime=101,
        )
        film1.countries = [pt, us]
        film1.spoken_languages = [en]
        film1.genres = [drama, history]

        db.session.add_all([
            Cast(person=actor1, film=film1, character="Hero", order=0),
            Cast(person=actor2, film=film1, character="Hero", order=1),
            Crew(person=director1, film=film1, role="director"),
            Crew(person=director1, film=film1, role="writer"),
            Crew(person=director1, film=film1, role="composer"),
            Crew(person=director1, film=film1, role="cinematographer"),
            Screening(film=film1, cinema=cinema2, first_seen=datetime(2023, 1, 1), last_seen=datetime.today()),
            Release(film=film1, country_id="PT", title="Full Film", date=datetime(2023, 1, 1), popularity=12.0)
        ])

        # FILM 2: MINIMAL DATA
        film2 = Film(
            id="film-2",
            title="Minimal Film",
            original_title="Minimal Film",
            original_language="en",
            content_rating="M/16",
            distributor="Cinemundo",
            runtime=96,
            release_year=2024
        )
        film2.genres = [drama]

        db.session.add(
            Release(film=film2, country_id="US", title="Minimal Film", date=datetime(2023, 9, 1), popularity=1.0)
        )

        # FILM 3: MULTI LANGUAGE + NO PT RELEASE
        film3 = Film(
            id="film-3",
            title="International Film",
            original_title="International Film",
            original_language="fr",
            content_rating="M/12",
            distributor="CinemasNOS",
            runtime=88,
            release_date=datetime(2023, 5, 1),
            release_year=2023
        )
        film3.spoken_languages = [fr, en]
        film3.countries = [us]

        db.session.add_all([
            Crew(person=director1, film=film3, role="director"),
            Cast(person=actor1, film=film3, character="Hero 1", order=0),
            Cast(person=actor2, film=film3, character="Hero 2", order=1),
            Release(film=film3, title="International Film", country_id="PT", date=datetime(2023, 5, 1), popularity=1.0)
        ])
        # No PT release → tests `.upcoming == False`

        # FILM 4: FUTURE FILM (tests upcoming=True)
        future_date = datetime.today().replace(year=datetime.now().year + 1)

        film4 = Film(
            id="film-4",
            title="Future Film",
            original_title="Future Film",
            original_language="en",
            content_rating="M/6",
            distributor="Nimas",
            runtime=131,
            release_year=2026
        )

        db.session.add_all([
            Crew(person=director2, film=film4, role="director"),
            Crew(person=director2, film=film4, role="writer"),
            Cast(person=actor2, film=film4, character="Hero 2", order=0),
            Release(film=film4, title="Future Film", country_id="PT", date=future_date, popularity=1.0)
        ])

        db.session.add_all([film1, film2, film3, film4])
        db.session.commit()
