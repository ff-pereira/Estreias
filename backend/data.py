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
    insert_countries_db, check_if_cinema_exists, insert_cinema_db, get_cinemas_ids_list, get_film_ids_between_periods

FILMSPOT_URL = "https://filmspot.pt"

FILMS_JSON_DIR = "api/static/films"
POSTERS_DIR = "api/static/images/posters"

FETCH_DELAY = 15
FETCH_RETRIES = 5
SLEEP_BETWEEN_MONTHS = 30

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


def generate_search_periods(past, future):
    """
    Returns a list of (label, is_year_mode, target_date)
    Generate search periods based on past and future months.
    If past or future exceeds 12 months, use year mode.
    :param past: Number of past months
    :param future: Number of future months
    :return: List of tuples (label, is_year_mode, target_date)
    """
    today = date.today()
    start_date = today - relativedelta(months=past)
    end_date = today + relativedelta(months=future)
       
    use_year_mode = past > 12 or future > 12
    
    periods = []
    
    if use_year_mode:
        years = range(start_date.year, end_date.year + 1)
        for year in years:
            periods.append((str(year), True, date(year, 1, 1)))
    else:
        total_months = past + 1 + future
        for i in range(total_months):
            # target = start_date + relativedelta(months=i)
            target = (start_date + relativedelta(months=i)).replace(day=1)
            label = f"{target.year}{target.month:02d}"
            periods.append((label, False, target))
        
    return periods


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


def parse_film(film_id, release_date, check_existing_posters):
    """
        Parse film data from Filmspot page.
        :param film_id: Film ID to parse
        :param release_date: Release date of the film
        :param check_existing_posters: If True, skip downloading posters if they already exist
        :return: Parsed film data as a dictionary or None if failed
    """
    film = {"id": film_id, "releaseDate": release_date}

    response = fetch_html(SESSION, FILMSPOT_URL + "/filme/" + film_id)
    if response is None:
        logging.error(f"Skipping film {film_id} due to fetch failure.")
        return None

    soup = BeautifulSoup(response, "html.parser")

    film["cinemas"], film["comingSoonCinemas"] = get_cinemas(soup)

    contents = soup.find("div", id="contents")

    if not contents:
        print(response)

    distributor_pt_div = contents.find("div", class_="caixaPais caixaPaisPortugal")
    distributor_p = distributor_pt_div.find('b', string='Distribuidor')
    if distributor_p:
        distributor_data = distributor_p.find_parent('p')
        distributor = distributor_data.get_text(strip=True).split('Distribuidor')[-1].strip()
    else:
        distributor = None

    film["distributor"] = distributor if distributor and distributor != "-" else None

    scripts = contents.find_all("script", type="application/ld+json")
    parsed_data = []

    for script in scripts:
        parsed_data.append(json.loads(script.string))

    film["tmdbId"] = film["id"].split("-")[-1]
    film["imdbId"] = parsed_data[1]["@graph"]["sameAs"].replace("http://www.imdb.com/title/", "").replace("/", "")

    title = parsed_data[1]["@graph"]["name"]
    clean_title = re.sub(r"\(\d{4}\)", "", title)
    clean_title = clean_title.strip()
    original_title = clean_title.split(" / ")[1] if " / " in clean_title else clean_title

    film["portugueseTitle"] = clean_title.split(" / ")[0] if " / " in title else clean_title
    film["originalTitle"] = clean_title.split(" / ")[1] if " / " in title else film["portugueseTitle"]

    film["contentRating"] = parsed_data[1]["@graph"]["contentRating"]
    film["year"] = parsed_data[1]["@graph"].get("copyrightYear", None)

    desc = parsed_data[1]["@graph"].get("description")
    film["portugueseDescription"] = BeautifulSoup(
        html.unescape(parsed_data[1]["@graph"].get("description") or ""),
        "html.parser").get_text() if desc else ""

    film["tmdbData"] = get_film_info(film["imdbId"], film["tmdbId"], original_title)

    if film["tmdbData"] is None:
        error_logger.error(f"No data found for film ID {film['id']}, {title}, tmdb ({film['tmdbId']}), release date: {release_date}")
        return None

    poster_types = {
        "pt": film["tmdbData"].get("portuguesePoster", None),
        "original": film["tmdbData"].get("poster", None),
        "backdrop": film["tmdbData"].get("backdrop", None),
    }

    for poster_type, url in poster_types.items():
        if url:
            download_poster(url, film["id"], poster_type, check_existing=check_existing_posters)

    return film


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
            slug = a_tag["href"].split("/filme/")[1].rstrip("/")
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

    message = f"From {len(all_film_ids)} films in cinemas to {in_cinemas_count}\nTook {round(time.time() - start_time, 2)} seconds"
    logging.info(message)
    requests.post(NTFY_TOPIC, data=message.encode('utf-8'), headers=NTFY_SUCCESS_HEADERS)


def update_films(past, future):
    """
        Update films data for past and future months.
        :param past: Number of past months to update
        :param future: Number of future months to update
    """
    start_time = time.time()

    new, updated = 0, 0

    periods = generate_search_periods(past, future)

    period_film_ids = get_film_ids_between_periods(periods)
    print(len(period_film_ids))

    all_section_film_ids = set()
    
    for idx, (current_search, is_year_mode, target_date) in enumerate(periods):
        check_existing_posters = not is_year_mode and (idx < past - 1) # Only reuse posters for past months older than 1 month
        logging.info(f"Updating: {current_search}, Replacing posters: {not check_existing_posters}. Year mode: {is_year_mode}.")

        response = fetch_html(SESSION, FILMSPOT_URL + "/estreias/" + current_search)

        if response is None:
            logging.error(f"Skipping month {current_search} due to fetch failure.")
            continue

        soup = BeautifulSoup(response, "html.parser")

        release_sections = soup.find_all('h2', class_='estreiasH2')

        for section in release_sections:
            section_id = section.get('id', '')
            date_str = section_id.replace('estreiasH2', '')
            release_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}" if len(date_str) == 8 else "Unknown"

            # Find all film entries
            container = section.find_next_sibling('div')
            section = container.find_all('div', class_='filmeLista')

            for film_page_html in section:
                filmeListaInfo = film_page_html.find("div", class_="filmeListaInfo")
                href = filmeListaInfo.find("h3").find("a").get("href")
                film_id = href.split("/")[2]

                all_section_film_ids.add(film_id)
                parsed_film = parse_film(film_id, release_date, check_existing_posters)

                if parsed_film is None:
                    continue

                with open(os.path.join(FILMS_JSON_DIR, f"{parsed_film['id']}.json"), "w", encoding="utf-8") as film_file:
                    film_file.write(json.dumps(parsed_film, ensure_ascii=False))

                in_cinemas = len(parsed_film.get("cinemas")) > 0

                new_film = add_film(parsed_film)
                if new_film:
                    new += 1
                    logging.info(f"Added new film: {parsed_film['id']}, Release date: {release_date}, In cinemas: {in_cinemas}")
                else:
                    updated += 1
                    logging.info(f"Updated film: {parsed_film['id']}, Release date: {release_date}, In cinemas: {in_cinemas}")

        logging.info(f"Finished updating month: {current_search}. Sleeping for {SLEEP_BETWEEN_MONTHS} seconds to avoid rate limiting.")
        time.sleep(SLEEP_BETWEEN_MONTHS)

    expired = remove_expired_releases(list(all_section_film_ids), period_film_ids)
    if expired:
       logging.info(f"{expired} are expired releases to remove.")
    else:
       logging.info("Current releases are the same as saved releases. No expired releases to remove.")

    message = f"Updated {past+future} months\nAdded: {new}\nUpdated: {updated}\nTook {round(time.time() - start_time, 2)} seconds"
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
            future_months = int(sys.argv[1])
            logging.info(f"Updating Screenings and {future_months} future months plus past and current")
            update_screenings()
            update_films(1, future_months)
        else:
            past_months = int(sys.argv[1])
            future_months = int(sys.argv[2])
            logging.info(f"Updating {past_months} past, current and {future_months} future months")
            update_films(past_months, future_months)
    except Exception as e:
        error_message = f"Script failed: {type(e).__name__}: {e}"
        error_logger.exception(error_message)

        requests.post(NTFY_TOPIC, data=error_message.encode('utf-8'), headers=NTFY_ERROR_HEADERS)
