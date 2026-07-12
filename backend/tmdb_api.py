"""
    author: ffpereira
    date: 2025-10-06
"""
import json
import os
import requests
from bs4 import BeautifulSoup
from rapidfuzz import fuzz
from dotenv import load_dotenv
from logger_config import logging

load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))
TMDB_API_KEY = os.environ.get('TMDB_API_KEY')


def get_person_info(person_id):
    resp = requests.get(
        f"https://api.themoviedb.org/3/person/{person_id}",
        params={"api_key": TMDB_API_KEY, "language": "en-US"}
    )

    if resp.status_code != 200:
        logging.error(f"Failed to fetch person data for ID {person_id}: {resp.status_code}")
        return None

    json_response = resp.json()

    if not json_response:
        logging.warning(f"No tmdb data found for person ID: {person_id}")
        return None

    return {
        "name": json_response.get('name', None),
        "gender": json_response.get('gender', None),
        "imdb_id": json_response.get('imdb_id', None),
        "biography": json_response.get('biography', None),
        "birthday": json_response.get('birthday', None),
        "deathday": json_response.get('deathday', None),
        "popularity": json_response.get('popularity', 0.0),
        "pob": json_response.get('place_of_birth', None),
        "known_for_department": json_response.get('known_for_department', None),
        "profile_path": json_response.get('profile_path', None),
    }


def get_film_info(tmdb_id, title, imdb_id=False):
    json_response = fetch_tmdb_movie(tmdb_id, title, imdb_id)

    if not json_response:
        return None

    # Man data
    origin_countries = json_response.get('origin_country', [])
    description = json_response.get('overview', '')
    original_release_date = json_response.get('release_date', None)
    spoken_languages = json_response.get('spoken_languages', [])
    original_language = json_response.get('original_language', None)
    title = json_response.get('title', None)
    genres = json_response.get('genres', [])
    runtime = json_response.get('runtime', 0)
    tagline = json_response.get('tagline', '')
    tmdb_id = json_response.get('id', None)

    # Financial data
    budget = json_response.get('budget', 0)
    revenue = json_response.get('revenue', 0)

    # Posters and Backdrop
    backdrop = json_response.get('backdrop_path', None)
    original_poster = json_response.get('poster_path', None)
    original_poster_path = f'https://image.tmdb.org/t/p/w500{original_poster}'
    backdrop_path = f'https://image.tmdb.org/t/p/original{backdrop}'

    pt_poster_response = requests.get(f"https://api.themoviedb.org/3/movie/{tmdb_id}/images?api_key={TMDB_API_KEY}&language=pt")
    pt_json_response = pt_poster_response.json()
    portuguese_posters = pt_json_response.get('posters', None)
    if portuguese_posters:
        portuguese_poster = portuguese_posters[0].get('file_path', None)
    else:
        portuguese_poster = None
    portuguese_poster_path = f'https://image.tmdb.org/t/p/w500{portuguese_poster}' if portuguese_posters else None

    # Cast and Crew data
    credits_response = requests.get(f"https://api.themoviedb.org/3/movie/{tmdb_id}/credits?api_key={TMDB_API_KEY}&language=en")
    credits_json_response = credits_response.json()

    cast_json = credits_json_response.get('cast', [])
    cast_dict = {}
    for actor in cast_json:
        actor_id = actor.get('id')
        if actor_id is None or actor_id in cast_dict:
            continue
        cast_dict[actor_id] = {
            "id": actor_id,
            "name": actor.get('name'),
            "original_name": actor.get('original_name'),
            "gender": actor.get('gender'),
            "character": actor.get('character'),
            "order": actor.get('order'),
        }
    cast = list(cast_dict.values())

    directors_dict, writers_dict, composers_dict, cinematographers_dict = {}, {}, {}, {}
    crew_json = credits_json_response.get('crew', [])
    for crew_member in crew_json:
        job = crew_member.get('job')
        crew_id = crew_member.get('id')

        if crew_id is None:
            continue

        crew_data = {
            "id": crew_id,
            "name": crew_member.get('name'),
            "original_name": crew_member.get('original_name'),
            "gender": crew_member.get('gender'),
        }

        if job == 'Director':
            if crew_id not in directors_dict:
                directors_dict[crew_id] = crew_data

        elif job == 'Screenplay':
            if crew_id not in writers_dict:
                writers_dict[crew_id] = crew_data

        elif job == 'Original Music Composer':
            if crew_id not in composers_dict:
                composers_dict[crew_id] = crew_data

        elif job == 'Director of Photography':
            if crew_id not in cinematographers_dict:
                cinematographers_dict[crew_id] = crew_data

    directors = list(directors_dict.values())
    writers = list(writers_dict.values())
    composers = list(composers_dict.values())
    cinematographers = list(cinematographers_dict.values())

    return {
        "tmdb_id": tmdb_id,
        "budget": budget,
        "revenue": revenue,
        "poster": original_poster_path,
        "portuguesePoster": portuguese_poster_path,
        "backdrop": backdrop_path,
        "originCountries": origin_countries,
        "description": description,
        "originalReleaseDate": original_release_date,
        "spokenLanguages": spoken_languages,
        "originalLanguage": original_language,
        "title": title,
        "cast": cast,
        "directors": directors,
        "writers": writers,
        "composers": composers,
        "cinematographers": cinematographers,
        "genres": genres,
        "runtime": runtime,
        "tagline": tagline,
        "imdb_id": json_response.get('imdb_id', None),
        "popularity": json_response.get('popularity', 0.0),
        "original_title": json_response.get('original_title', None),
    }

"""
def fetch_tmdb_movie(imdb_id, tmdb_id, original_title):

    def fetch_movie_by_id(movie_id):
        resp = requests.get(
            f"https://api.themoviedb.org/3/movie/{movie_id}",
            params={"api_key": TMDB_API_KEY, "language": "en-US"}
        )
        return resp.json()

    def validate_title_match(local_title, candidate_title, threshold):
        ratio = fuzz.token_set_ratio(local_title.lower(), candidate_title.lower())
        if candidate_title and ratio >= threshold:
            logging.info(f"Titles are similar enough, proceeding successfully.")
            return True
        else:
            logging.warning(f"Title mismatch: provided '{original_title}', obtained '{candidate_title}' (ratio: {ratio})")
            return None

    json_response = None
    original_title_local = original_title.strip()

    # Case 0: IMDb ID missing — fetch directly by TMDB ID
    if not imdb_id:
        logging.info("No IMDb ID provided, fetching by TMDB ID directly.")
        tmdb_response = fetch_movie_by_id(tmdb_id)

        if not tmdb_response or not tmdb_response.get("success", True):
            logging.warning(f"TMDB request failed or movie not found: {tmdb_response}")
            return None

        response_title = tmdb_response.get("title", "").strip()
        if not response_title:
            logging.warning(f"No title found for TMDB ID {tmdb_id}")
            return None

        # Compare titles — if mismatch, fall back to title search
        logging.info(f"Comparing titles {original_title_local} and {response_title}")
        if not validate_title_match(original_title_local, response_title, 70):
            logging.warning("TMDB title check failed.")
            return None

        return tmdb_response

    response = requests.get(f"https://api.themoviedb.org/3/find/{imdb_id}?api_key={TMDB_API_KEY}&external_source=imdb_id")
    data = response.json()

    # Case 1: No movie_results
    if not data["movie_results"]:
        logging.info(f"No movie results found for IMDb ID: {imdb_id}")
        json_response = fetch_movie_by_id(tmdb_id)

        if not json_response or not json_response.get("success", True):
            logging.warning(f"TMDB request failed or movie not found: {json_response}")
            return None

        if json_response.get("adult") is True:
            logging.warning("TMDB ID is adult content")
            return None

        tmdb_title = json_response.get('original_title', "")
        if tmdb_title:
            # Compare titles — if mismatch, fall back to title search
            logging.info(f"Comparing titles {original_title_local} and {tmdb_title.strip()}")
            if not validate_title_match(original_title_local, tmdb_title.strip(), 70):
                logging.warning("TMDB title check failed.")
                return None
        else:
            return None

    # Case 2: movie_results exist
    else:
        obtained_tmdb_id = data["movie_results"][0]["id"]
        if int(tmdb_id) != int(obtained_tmdb_id):
            logging.info(f"TMDB ID mismatch: provided {tmdb_id}, obtained {obtained_tmdb_id}, checking IMDb IDs")
            json_response = fetch_movie_by_id(obtained_tmdb_id)

            if not json_response or not json_response.get("success", True):
                logging.warning(f"TMDB request failed or movie not found: {json_response}")
                return None

            if imdb_id and imdb_id != json_response.get('imdb_id', ''):
                logging.warning(f"IMDb ID mismatch: provided '{imdb_id}', obtained '{json_response.get('imdb_id', '')}'")
                return None
            else:
                logging.info("IMDb IDs match successfully, proceeding with provided TMDB ID.")

    if not json_response:
        json_response = fetch_movie_by_id(tmdb_id)

        if not json_response or not json_response.get("success", True):
            logging.warning(f"TMDB request failed or movie not found: {json_response}")
            return None

    return json_response
"""


def fetch_tmdb_movie(tmdb_id, title, imdb_id=False):
    def fetch_movie_by_id(movie_id):
        resp = requests.get(
            f"https://api.themoviedb.org/3/movie/{movie_id}",
            params={"api_key": TMDB_API_KEY, "language": "en-US"}
        )
        return resp.json()

    def fetch_movie_by_title(title):
        resp = requests.get(
            f"https://api.themoviedb.org/3/search/movie",
            params={"api_key": TMDB_API_KEY, "query": title, "include_adult": "false", "language": "pt-PT"}
        )
        return resp.json()

    def fetch_movie_by_imdb(imdb_id):
        resp = requests.get(f"https://api.themoviedb.org/3/find/{imdb_id}",
            params={ "api_key": TMDB_API_KEY, "language": "en-US", "external_source": "imdb_id"}
        )
        return resp.json()

    if not imdb_id:
        tmdb_title_response = fetch_movie_by_title(title)

        if tmdb_title_response and tmdb_title_response.get("results"):
            first_result_id = tmdb_title_response["results"][0]["id"]
            first_result_title = tmdb_title_response["results"][0].get("title", "")

            if int(first_result_id) != int(tmdb_id):
                logging.warning(f"TMDB ID mismatch: provided {tmdb_id} ({title}), obtained {first_result_id} ({first_result_title}) from title search.")
                return None
    else:
        tmdb_imdb_response = fetch_movie_by_imdb(imdb_id)

        if not tmdb_imdb_response["movie_results"]:
            return None
        else:
            tmdb_id = tmdb_imdb_response["movie_results"][0]["id"]

    tmdb_response = fetch_movie_by_id(tmdb_id)

    if tmdb_response and tmdb_response.get("success", True):
        if tmdb_response.get("adult"):
            logging.warning(f"Excluded adult movie: {tmdb_response.get('title')}")
            return None
        return tmdb_response
    else:
        logging.warning(f"TMDB request failed or movie not found for TMDB ID {tmdb_id}: {tmdb_response}")
        return None
