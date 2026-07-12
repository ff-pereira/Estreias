"""
    author: ffpereira
    date: 2025-10-06
"""


import os
import json

import requests
from dotenv import load_dotenv
from sqlalchemy import create_engine, func, desc, extract
from sqlalchemy.orm import sessionmaker
from datetime import date, datetime, timezone
from sqlalchemy import orm as so

from api.models import Film, Genre, Country, Cinema, Crew, Person, film_genres, film_countries, Screening, film_spoken_languages, Language, Cast, Release

load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))
ALCHEMICAL_DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(ALCHEMICAL_DATABASE_URL)
Session = sessionmaker(bind=engine)
db = Session()


def get_top_persons(role, limit):
    top_persons = (
        db.query(Person.id)
        .join(role)
        .filter(Person.updated_at == None)
        .group_by(Person.id)
        .order_by(desc(func.count(role.film_id)),Person.id.asc())
        .limit(limit)
        .all()
    )
    return [person_id[0] for person_id in top_persons]


def get_last_updated_persons(role, limit):
    last_updated_persons = (
        db.query(Person.id)
        .join(role)
        .filter(Person.updated_at != None)
        .group_by(Person.id)
        .order_by(Person.updated_at.asc())
        .limit(limit)
        .all()
    )
    return [person_id[0] for person_id in last_updated_persons]


def get_in_cinemas_film_ids():
    Film_ids = db.query(Film.id).filter(Film.in_cinemas == True).all()
    return [film_id[0] for film_id in Film_ids]


def remove_expired_releases(new_tmdb_ids, year):
    new_tmdb_ids = set(new_tmdb_ids)

    db_ids = {
        film_id[0]
        for film_id in db.query(Release.film_id)
        .filter(
            Release.country_id == 'PT',
            extract('year', Release.date) == year
        )
        .all()
    }

    ids_to_delete = db_ids - new_tmdb_ids

    if not ids_to_delete:
        return 0

    deleted_count = (
        db.query(Release)
        .filter(
            Release.country_id == 'PT',
            extract('year', Release.date) == year,
            Release.film_id.in_(ids_to_delete)
        )
        .delete(synchronize_session=False)
    )
    db.commit()

    return deleted_count or 0


def add_film(film_json):

    is_new_film = True

    tmdb_data = film_json.get('tmdbData') or {}
    f_id = film_json['id']

    def safe_list(d, key):
        return d.get(key) or []

    # --- 1. PRE-FETCH FILM ---
    film = db.query(Film).options(
        so.selectinload(Film.genres),
        so.selectinload(Film.countries),
        so.selectinload(Film.spoken_languages),
        so.selectinload(Film.cast),
        so.selectinload(Film.crew)
    ).filter(Film.id == f_id).first()

    # --- 2. PRE-FETCH PEOPLE ---
    person_ids = {c['id'] for c in safe_list(tmdb_data, 'cast')}

    for k in ['directors', 'writers', 'composers', 'cinematographers']:
        person_ids.update(p['id'] for p in safe_list(tmdb_data, k))

    existing_persons = {
        p.id: p
        for p in db.query(Person)
        .filter(Person.id.in_(list(person_ids)))
        .all()
    }

    # --- 3. FILM ATTRIBUTES ---
    film_attrs = {
        "release_date": tmdb_data.get('originalReleaseDate') or None,
        "title": tmdb_data.get('title') or film_json.get('originalTitle'),
        "original_title": tmdb_data.get('original_title') or None,
        "portuguese_title": film_json.get('portugueseTitle'),
        "runtime": tmdb_data.get('runtime'),
        "budget": tmdb_data.get("budget"),
        "revenue": tmdb_data.get("revenue"),
        "content_rating": film_json.get('contentRating'),
        "description": tmdb_data.get('description'),
        "portuguese_description": film_json.get('portugueseDescription'),
        "imdb_id": tmdb_data.get('imdb_id') or film_json.get('imdbId'),
        "tagline": tmdb_data.get('tagline'),
        "distributor": film_json.get('distributor'),
        "release_year": film_json.get("year"),
        "tmdb_id": tmdb_data.get('tmdb_id'),
        "in_cinemas": film.in_cinemas if film else False,
        "original_language": tmdb_data.get('originalLanguage') or None
    }

    if not film:
        film = Film(id=f_id, **film_attrs)
        db.add(film)
    else:
        is_new_film = False
        for key, value in film_attrs.items():
            setattr(film, key, value)

    # --- 4. GENRES ---
    curr_genres = {g.id for g in film.genres}

    for g_j in safe_list(tmdb_data, 'genres'):
        if g_j['id'] not in curr_genres:
            genre = db.get(Genre, g_j['id']) or Genre(id=g_j['id'], name=g_j['name'])
            film.genres.append(genre)

    # --- 5. COUNTRIES ---
    curr_countries = {c.id for c in film.countries}

    for c_id in safe_list(tmdb_data, 'originCountries'):
        if c_id not in curr_countries:
            country = db.get(Country, c_id) or Country(id=c_id)
            film.countries.append(country)

    # --- 6. CAST ---
    curr_cast = {c.person_id: c for c in film.cast}

    for c_j in safe_list(tmdb_data, 'cast'):
        p_id = c_j['id']

        if p_id not in existing_persons:
            p = Person(
                id=p_id,
                name=c_j.get('name'),
                original_name=c_j.get('original_name'),
                gender=c_j.get('gender')
            )
            db.add(p)
            existing_persons[p_id] = p

        if p_id in curr_cast:
            curr_cast[p_id].character = c_j.get('character')
            curr_cast[p_id].order = c_j.get('order')
        else:
            film.cast.append(
                Cast(
                    person_id=p_id,
                    character=c_j.get('character'),
                    order=c_j.get('order')
                )
            )

    # --- 7. CREW ---
    curr_crew = {(cr.person_id, cr.role) for cr in film.crew}

    roles = {
        'directors': 'director',
        'writers': 'writer',
        'composers': 'composer',
        'cinematographers': 'cinematographer'
    }

    for key, role_name in roles.items():
        for cr_j in safe_list(tmdb_data, key):
            p_id = cr_j['id']

            if p_id not in existing_persons:
                p = Person(
                    id=p_id,
                    name=cr_j.get('name'),
                    original_name=cr_j.get('original_name'),
                    gender=cr_j.get('gender')
                )
                db.add(p)
                existing_persons[p_id] = p

            if (p_id, role_name) not in curr_crew:
                film.crew.append(Crew(person_id=p_id, role=role_name))

    # --- 8. LANGUAGE ---
    if film.original_language:
        if not db.get(Language, film.original_language):
            db.add(Language(id=film.original_language))

    # --- 9. RELEASE ---
    release = db.query(Release).filter_by(
        film_id=f_id,
        country_id='PT'
    ).first()

    if not release:
        db.add(Release(
            film_id=f_id,
            country_id='PT',
            date=film_json.get('releaseDate'),
            title=film_json.get('portugueseTitle'),
            popularity=tmdb_data.get('popularity')
        ))
    else:
        release.date = film_json.get('releaseDate')
        release.title = film_json.get('portugueseTitle')
        release.popularity = tmdb_data.get('popularity')

    # --- 10. SCREENINGS ---
    # update_screenings_db(f_id, film_json.get('cinemas'))

    db.commit()
    return is_new_film


def update_screenings_db(film_id, cinemas):
    """
        Update screenings in the database for a given film and list of cinemas.
        :param film_id: ID of the film.
        :param cinemas: List of cinema JSON objects.
        :return: None
    """
    film = db.query(Film).filter(Film.id == film_id).first()

    if not film:
        return

    db.query(Film).filter(Film.id == film_id).update({"in_cinemas": len(cinemas) > 0})

    for cinema_json in cinemas:
        cinema = db.query(Cinema).filter(Cinema.id == cinema_json['id']).first()
        if not cinema:
            cinema = Cinema(
                id=cinema_json['id'],
                name=cinema_json['name'],
            )
            db.add(cinema)
            db.flush()

        screening = db.query(Screening).filter(
            Screening.film_id == film_id,
            Screening.cinema_id == cinema_json['id']
        ).first()

        if not screening:
            screening = Screening(
                film_id=film_id,
                cinema_id=cinema_json['id'],
                first_seen=date.today(),
                last_seen=date.today()
            )
            db.add(screening)
        else:
            screening.last_seen = date.today()

    db.commit()


def update_person(person_id, person_data):
    """
        Update person information in the database.
        :param person_id: ID of the person.
        :param person_data: Dictionary containing person data.
    """
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        return False

    fields = ['name', 'gender', 'imdb_id', 'popularity', 'birthday',
              'deathday', 'pob', 'biography', 'known_for_department']
    for field in fields:
        if field in person_data:
            setattr(person, field, person_data[field])

    person.updated_at = datetime.now(timezone.utc)

    db.commit()

    return True


def insert_countries_db(countries_path):
    """
        Insert countries into the database from a JSON file.
        :return: None
    """
    with open(countries_path, 'r', encoding='utf-8') as f:
        countries_dict = json.load(f)
    for country_code, country_name in countries_dict.items():
        country = db.query(Country).filter(Country.id == country_code).first()
        if not country:
            country = Country(
                id=country_code,
                name=country_name
            )
            db.add(country)
    db.commit()


def check_if_cinema_exists(cinema_id):
    """
        Check if a cinema exists in the database.
        :param cinema_id: ID of the cinema.
        :return: True if cinema exists, False otherwise.
    """
    return db.query(Cinema).filter(Cinema.id == cinema_id).first() is not None


def insert_cinema_db(cinema_data):
    """
        Insert a cinema into the database.
        :param cinema_data: data of the cinema.
        :return: None
    """
    if not check_if_cinema_exists(cinema_data["id"]):
        country = db.query(Country).filter(func.lower(Country.name) == func.lower(cinema_data["addressCountry"])).first()
        if country:
            cinema_data["countryId"] = country.id
        else:
            cinema_data["countryId"] = None

        cinema_data["group"] = None
        if "Cinemas NOS" in cinema_data["name"]:
            cinema_data["group"] = "Cinemas NOS"
        elif "Castello Lopes" in cinema_data["name"]:
            cinema_data["group"] = "Castello Lopes"
        elif "UCI Cinemas" in cinema_data["name"]:
            cinema_data["group"] = "UCI Cinemas"
        elif "Cinema City" in cinema_data["name"]:
            cinema_data["group"] = "Cinema City"
        elif "Cineplace" in cinema_data["name"]:
            cinema_data["group"] = "Cineplace"

        cinema = Cinema(
            id=cinema_data["id"],
            name=cinema_data["name"],
            latitude=cinema_data["latitude"],
            longitude=cinema_data["longitude"],
            street_address=cinema_data["streetAddress"],
            postal_code=cinema_data["postalCode"],
            address_region=cinema_data["addressRegion"],
            address_locality=cinema_data["addressLocality"],
            address_country=cinema_data["addressCountry"],
            telephone=cinema_data["telephone"],
            country_id=cinema_data["countryId"],
            group=cinema_data["group"]
        )
        db.add(cinema)
        db.commit()
    else:
        cinema = db.query(Cinema).filter(Cinema.id == cinema_data["id"]).first()
        cinema.name = cinema_data["name"]
        cinema.latitude = cinema_data["latitude"]
        cinema.longitude = cinema_data["longitude"]
        cinema.street_address = cinema_data["streetAddress"]
        cinema.postal_code = cinema_data["postalCode"]
        cinema.address_region = cinema_data["addressRegion"]
        cinema.address_locality = cinema_data["addressLocality"]
        cinema.address_country = cinema_data["addressCountry"]
        cinema.telephone = cinema_data["telephone"]
        country = db.query(Country).filter(func.lower(Country.name) == func.lower(cinema_data["addressCountry"])).first()
        if country:
            cinema.country_id = country.id
        else:
            cinema.country_id = None

        if "Cinemas NOS" in cinema_data["name"]:
            cinema.group = "Cinemas NOS"
        elif "Castello Lopes" in cinema_data["name"]:
            cinema.group = "Castello Lopes"
        elif "UCI Cinemas" in cinema_data["name"]:
            cinema.group = "UCI Cinemas"
        elif "Cinema City" in cinema_data["name"]:
            cinema.group = "Cinema City"
        elif "Cineplace" in cinema_data["name"]:
            cinema.group = "Cineplace"

        db.commit()




def get_cinemas_ids_list():
    """
        Get a list of all cinema IDs in the database.
        :return: List of cinema IDs.
    """
    cinema_ids = db.query(Cinema.id).all()
    return [cinema_id[0] for cinema_id in cinema_ids]
