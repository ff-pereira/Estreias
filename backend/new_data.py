"""
    author: ffpereira
    date: 2025-10-06
"""

import os
import re
import sys
import json
import html
import requests
import time
from bs4 import BeautifulSoup
from datetime import date
from dateutil.relativedelta import relativedelta

from tmdb_api import get_film_info
from logger_config import logging, error_logger
from repository import add_film, get_in_cinemas_film_ids, update_screenings_db, remove_expired_releases, \
    insert_countries_db, check_if_cinema_exists, insert_cinema_db, get_cinemas_ids_list

FILMSPOT_URL = "https://filmspot.pt"

FILMS_JSON_DIR = "api/static/films"
POSTERS_DIR = "api/static/images/posters"

FETCH_DELAY = 15
FETCH_RETRIES = 5
SLEEP_BETWEEN_YEARS = 60

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
})

NTFY_TOPIC = 'https://ntfy.sh/ffpereira-estreias'
NTFY_SUCCESS_HEADERS = {
    "Title": "Estreias Data Updated",
    "Tags": "white_check_mark"
}
NTFY_ERROR_HEADERS = {
    "Title": "Estreias Data Update Errors",
    "Tags": "x"
}


def fetch_html(session, url, retries=FETCH_RETRIES, delay=FETCH_DELAY):
    """
        Fetch HTML content from a URL with retries and delay.
        :param session: requests.Session object
        :param url: URL to fetch
        :param retries: Number of retries
        :param delay: Delay between retries in seconds
        :return: HTML content as text or None if failed
    """
    for attempt in range(1, retries + 1):
        try:
            r = session.get(url, allow_redirects=True, timeout=(3, 20))
            r.raise_for_status()
            return r.text
        except requests.RequestException as e:
            logging.error(f"Error fetching {url}. Attempt {attempt} failed for: {e}")
            time.sleep(delay * attempt)
    return None


def extract_cinema_data(cinema_id):
    url = f"{FILMSPOT_URL}/cinema/{cinema_id}"
    response = fetch_html(SESSION, url)

    soup = BeautifulSoup(response, "html.parser")

    result = {
        "id": cinema_id,
        "name": None,
        "latitude": None,
        "longitude": None,
        "streetAddress": None,
        "postalCode": None,
        "addressRegion": None,
        "addressLocality": None,
        "addressCountry": None,
        "telephone": None,
    }

    scripts = soup.find_all("script", type="application/ld+json")

    for script in scripts:
        try:
            data = json.loads(script.string)

            graph = data.get("@graph")
            if graph and graph.get("@type") == "MovieTheater":
                geo = graph.get("geo", {})
                address = graph.get("address", {})

                result["name"] = graph.get("name")
                result["latitude"] = geo.get("latitude")
                result["longitude"] = geo.get("longitude")
                result["streetAddress"] = address.get("streetAddress")
                result["postalCode"] = address.get("postalCode")
                result["addressRegion"] = address.get("addressRegion")
                result["addressLocality"] = address.get("addressLocality")
                result["addressCountry"] = address.get("addressCountry")
                result["telephone"] = address.get("telephone")

        except Exception:
            continue

    return result


def download_poster(poster_url, film_id, poster_type, check_existing=False):
    """
        Download poster image from URL and save it to the appropriate folder.
        :param poster_url: URL of the poster image
        :param film_id: Film ID to name the poster file
        :param poster_type: Type of poster ('pt', 'original', 'backdrop')
        :param check_existing: If True, skip download if poster already exists
    """
    folder_path = os.path.join(POSTERS_DIR, poster_type)
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, f"{film_id}.jpg")

    if check_existing and os.path.exists(file_path):
        logging.info(f"Poster already exists for film {film_id} with more than 30 days, skipping download.")
    else:
        response = SESSION.get(poster_url, timeout=(3, 20))
        if response.status_code == 200:
            with open(file_path, "wb") as f:
                f.write(response.content)
        else:
            error_logger.error(f"Failed to download {poster_type} poster for film {film_id} from {poster_url}. Status code: {response.status_code}")


def get_cinemas(film_soup):
    cinemas, coming_soon_cinemas = [], []
    cinemas_list = film_soup.find("div", id="filmeInfoDivSessoes")

    # Avoid cinemas where is coming soon
    if cinemas_list:
        cinemas_list_li, coming_soon_list_li = [], []
        brevemente_tag = cinemas_list.find("h2", string=lambda s: s and "Brevemente" in s)

        for li in cinemas_list.find_all("li"):
            if brevemente_tag and li.sourceline > brevemente_tag.sourceline:
                coming_soon_list_li.append(li)
            else:
                cinemas_list_li.append(li)

        for li in cinemas_list_li:
            cinema = {}
            cinema["id"] = li.find("a").get("href").split("/")[2]
            cinema["name"] = li.get_text(strip=True)

            cinema_exists = check_if_cinema_exists(cinema["id"])
            if not cinema_exists:
                logging.info(f"New cinema found: {cinema['name']} ({cinema['id']}). Adding to database.")
                cinema_data = extract_cinema_data(cinema["id"])
                insert_cinema_db(cinema_data)

            cinemas.append(cinema)

        for li in coming_soon_list_li:
            coming_soon_cinema = {}
            coming_soon_cinema["id"] = li.find("a").get("href").split("/")[2]
            coming_soon_cinema["name"] = li.get_text(strip=True)

            cinema_exists = check_if_cinema_exists(coming_soon_cinema["id"])
            if not cinema_exists:
                logging.info(f"New cinema found: {coming_soon_cinema['name']} ({coming_soon_cinema['id']}). Adding to database.")
                cinema_data = extract_cinema_data(coming_soon_cinema["id"])
                insert_cinema_db(cinema_data)

            coming_soon_cinemas.append(coming_soon_cinema)

    return cinemas, coming_soon_cinemas


def update_screenings():
    """
        Update screenings for films currently in cinemas.
    """
    start_time = time.time()

    previously_in_cinemas_film_ids = get_in_cinemas_film_ids()

    response = fetch_html(SESSION, FILMSPOT_URL + "/filmes/")
    soup = BeautifulSoup(response, "html.parser")

    in_cinemas_film_ids = []
    for div in soup.find_all("div", class_="filmeLista"):
        a_tag = div.find("a", href=True)
        if a_tag and a_tag["href"].startswith("/filme/"):
            slug = a_tag["href"].split("/filme/")[1].rstrip("/").split("-")[-1]
            in_cinemas_film_ids.append(slug)

    all_film_ids = list(set(previously_in_cinemas_film_ids) | set(in_cinemas_film_ids))

    logging.info(f"Updating Screenings of the {len(in_cinemas_film_ids)} films currently in cinemas. "
                 f"Yesterday Count: {len(previously_in_cinemas_film_ids)} Total films to check: {len(all_film_ids)}")

    in_cinemas_count = 0
    for idx, film_id in enumerate(all_film_ids, start=1):
        response = fetch_html(SESSION, FILMSPOT_URL + "/filme/" + film_id)
        if response is None:
            logging.error(f"Skipping film {film_id} in screenings due to fetch failure.")
            continue

        soup = BeautifulSoup(response, "html.parser")

        cinemas, _ = get_cinemas(soup)
        update_screenings_db(film_id, cinemas)

        in_cinemas = len(cinemas) > 0
        in_cinemas_count += in_cinemas

        percent = round((idx / len(all_film_ids)) * 100, 2)
        logging.info(f"{percent}%: In cinemas: {in_cinemas}, {film_id}")

    message = f"Films in cinemas: {in_cinemas_count}\nTook {round(time.time() - start_time, 2)} seconds"
    logging.info(message)
    requests.post(NTFY_TOPIC, data=message.encode('utf-8'), headers=NTFY_SUCCESS_HEADERS)


def fetch_imdb_id(film_id):
    url = f"{FILMSPOT_URL}/filme/{film_id}"
    response = fetch_html(SESSION, url)
    imdb_id = None

    if response is None:
        logging.error(f"Failed to fetch film page for {film_id} to get IMDb ID.")
        return None

    soup = BeautifulSoup(response, "html.parser")
    scripts = soup.find_all("script", type="application/ld+json")

    for script in scripts:
        try:
            data = json.loads(script.string)
            graph = data.get("@graph")

            if graph:
                if isinstance(graph, dict):
                    graph = [graph]

                for item in graph:
                    if item.get("@type") == "Movie":
                        same_as = item.get("sameAs")

                        if isinstance(same_as, list):
                            for url in same_as:
                                if "imdb.com/title/" in url:
                                    imdb_id = url.split("/title/")[1].strip("/")
                                    break
                        elif isinstance(same_as, str) and "imdb.com/title/" in same_as:
                            imdb_id = same_as.split("/title/")[1].strip("/")

                        if imdb_id:
                            break
        except Exception:
            continue

    if imdb_id:
        logging.info(f"Fetched IMDb ID for film {film_id}: {imdb_id}")
    else:
        logging.error(f"IMDb ID not found for film {film_id}.")

    return imdb_id


def update_films(year):
    """
        Update films data for past and future months.
        :param past: Number of past months to update
        :param future: Number of future months to update
    """
    new, updated = 0, 0
    all_tmdb_ids = set()

    start_time = time.time()
    check_existing_posters = False
    logging.info(f"Updating: {year}, Replacing posters: {not check_existing_posters}")

    response = fetch_html(SESSION, FILMSPOT_URL + "/estreias/" + year)

    if response is None:
        logging.error(f"Skipping year {year} due to fetch failure.")
        return

    soup = BeautifulSoup(response, "html.parser")
    release_sections = soup.find_all('h2', class_='estreiasH2')

    for section in release_sections:
        section_id = section.get('id', '')
        date_str = section_id.replace('estreiasH2', '')
        release_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}" if len(date_str) == 8 else "Unknown"

        # Find all film entries
        container = section.find_next_sibling('div')
        section = container.find_all('div', class_='filmeLista')

        section_film_ids, section_tmdb_ids = [], []

        for film_page_html in section:
            start_time_film = time.time()
            filmeListaInfo = film_page_html.find("div", class_="filmeListaInfo")
            href = filmeListaInfo.find("h3").find("a").get("href")
            title = filmeListaInfo.find("h3").find("a").find("span").get_text(strip=True)
            film_id = href.split("/")[2].split("-")[-1]

            section_film_ids.append(film_id)
            parsed_film = {"id": film_id, "releaseDate": release_date}

            def extract_labeled_value(container, label):
                for p in container.find_all("p"):
                    b = p.find("b")
                    if b and label in b.text:
                        return p.get_text(strip=True).replace(label, "").strip()
                return None

            parsed_film["portugueseTitle"] = filmeListaInfo.find("h3").find("a").find("span").get_text(strip=True)
            parsed_film["contentRating"] = extract_labeled_value(filmeListaInfo, "Class. etária")
            parsed_film["distributor"] = extract_labeled_value(filmeListaInfo, "Distribuidor")

            parsed_film["tmdbData"] = get_film_info(film_id, title)

            if parsed_film["tmdbData"] is None:
                # logging.warning(f"Failed to fetch TMDb data for film {film_id}. Trying to fetch imdb_id.")
                imdb_id = fetch_imdb_id(film_id)

                if imdb_id:
                    parsed_film["tmdbData"] = get_film_info(film_id, title, imdb_id)
                    if parsed_film["tmdbData"] is None:
                        logging.error(f"Failed to fetch TMDb data for film {film_id} using imdb_id. Skipping film")
                        continue
                else:
                    continue

            parsed_film["portugueseDescription"] = None
            # parsed_film["cinemas"] = []
            # parsed_film["comingSoonCinemas"] = []

            release_year = None
            info_p = filmeListaInfo.find_all("p", class_="zsmall")[0]
            if info_p:
                text = info_p.get_text(strip=True)
                release_year = text.split("|")[0].strip()
            parsed_film["year"] = release_year if release_year and release_year.isdigit() else None

            section_tmdb_ids.append(film_id)

            with open(os.path.join(FILMS_JSON_DIR, f"{parsed_film['id']}.json"), "w", encoding="utf-8") as film_file:
                film_file.write(json.dumps(parsed_film, ensure_ascii=False))
            
            poster_types = {
                "pt": parsed_film["tmdbData"].get("portuguesePoster", None),
                "original": parsed_film["tmdbData"].get("poster", None),
                "backdrop": parsed_film["tmdbData"].get("backdrop", None),
            }

            for poster_type, url in poster_types.items():
                if url:
                    download_poster(url, parsed_film["id"], poster_type, check_existing=check_existing_posters)

            # in_cinemas = False
            new_film = add_film(parsed_film)

            if new_film:
                new += 1
                logging.info(f"Added new film: {parsed_film['id']}, Release date: {release_date}, Took {round(time.time() - start_time_film, 2)} seconds, Title: {title}")
            else:
                updated += 1
                logging.info(f"Updated film: {parsed_film['id']}, Release date: {release_date}, Took {round(time.time() - start_time_film, 2)} seconds, Title: {title}")

        all_tmdb_ids.update(section_tmdb_ids)

    logging.info(f"Finished updating: {year}. Sleeping for {SLEEP_BETWEEN_YEARS} seconds to avoid rate limiting.")
    time.sleep(SLEEP_BETWEEN_YEARS)

    expired = remove_expired_releases(all_tmdb_ids, year)
    if expired:
        logging.info(f"{expired} are expired releases to remove.")
    else:
        logging.info("Current releases are the same as saved releases. No expired releases to remove.")

    message = f"Updated {year}\nAdded: {new}\nUpdated: {updated}\nDeleted: {expired}\nTook {round(time.time() - start_time, 2)} seconds"
    logging.info(message)
    requests.post(NTFY_TOPIC, data=message.encode('utf-8'), headers=NTFY_SUCCESS_HEADERS)


def insert_cinemas_db():
    cinemas_list = get_cinemas_ids_list()
    for cinema in cinemas_list:
        print(f"Adding cinema {cinema} to database.")
        cinema_data = extract_cinema_data(cinema)
        insert_cinema_db(cinema_data)


if __name__ == "__main__":
    #insert_countries_db("api/static/countries.json")
    #insert_cinemas_db()

    try:
        if len(sys.argv) == 1:
            logging.info("Updating Screenings")
            update_screenings()
        elif len(sys.argv) == 2:
            year_arg = sys.argv[1]
            logging.info(f"Updating {year_arg} year")
            update_films(year_arg)
        else:
            for arg in sys.argv[1:]:
                logging.info(f"Updating {arg} year")
                update_films(arg)
    except Exception as e:
        error_message = f"Script failed: {type(e).__name__}: {e}"
        error_logger.exception(error_message)

        requests.post(NTFY_TOPIC, data=error_message.encode('utf-8'), headers=NTFY_ERROR_HEADERS)
