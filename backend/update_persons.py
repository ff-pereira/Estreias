"""
    author: ffpereira
    date: 2025-10-06
"""

import os
import sys
import time
import requests

from tmdb_api import get_person_info
from logger_config import logging
from repository import get_top_persons, update_person, get_last_updated_persons

from api.models import Cast, Crew

PORTRAITS_DIR = 'api/static/images/persons'
TMDB_IMAGES = 'https://image.tmdb.org/t/p/'


def download_portrait(person_id, profile_path, size):
    """Download and save a person's portrait image from TMDB.

    Downloads the portrait image for a person from The Movie Database (TMDB)
    and saves it to the local static directory. Creates the target directory
    if it doesn't exist.

    Args:
        person_id (str): Unique identifier of the person
        profile_path (str): TMDB profile path for the person's image
        size (str): Image size to download. Must be 'w300' or 'w500'

    Returns:
        None

    Logs:
        ERROR: If invalid size is provided or download fails
    """
    if size not in ['w300', 'w500']:
        logging.error(f"Invalid size '{size}' for portrait download. Must be 'w300' or 'w500'.")
        return

    folder_path = os.path.join(PORTRAITS_DIR, size)

    if not os.path.exists(folder_path):
        os.makedirs(folder_path, exist_ok=True)

    file_path = os.path.join(folder_path, f"{person}.jpg")
    portrait_url = f"{TMDB_IMAGES}{size}{profile_path}"

    response = requests.get(portrait_url, timeout=(3, 20))
    if response.status_code == 200:
        with open(file_path, "wb") as f:
            f.write(response.content)
    else:
        logging.error(f"Failed to download {size} portrait for person {person_id} from {portrait_url}. Status code: {response.status_code}")


if __name__ == "__main__":
    """TMDB person data update script.

    Updates person information and downloads portraits from The Movie Database (TMDB).
    Supports updating either cast or crew members, with options to add new top persons
    or update recently modified persons.

    Usage:
        python update_persons.py [crew|cast] [add|update] [number_of_persons]

    Arguments:
        model_type: Either 'crew' or 'cast' to specify which table to update
        mode: 'add' to add top persons, 'update' to update recently modified persons
        number_of_persons: Integer specifying how many persons to process

    Example:
        python update_persons.py cast add 50
        python update_persons.py crew update 20
    """
    if len(sys.argv) != 4:
        print("Usage: python update_persons.py [crew|cast] [add|update] [number_of_persons]")
        sys.exit(1)

    model = Crew if sys.argv[1] == "crew" else Cast
    mode = "update" if sys.argv[2] == "update" else "add"

    try:
        number_of_persons = int(sys.argv[3])
    except ValueError:
        print(f"Error: number_of_persons must be an integer, got '{sys.argv[3]}'")
        sys.exit(1)

    if mode == "add":
        logging.info(f"Adding {number_of_persons} top persons from {sys.argv[1]}.")
        top_persons = get_top_persons(model, number_of_persons)
    else:
        logging.info(f"Updating {number_of_persons} last updated persons from {sys.argv[1]}.")
        top_persons = get_last_updated_persons(model, number_of_persons)

    start_time = time.time()
    updated_persons = 0
    for person in top_persons:
        data = get_person_info(person)

        if not data:
            logging.error(f"No data found for person ID {person}")
            continue

        status = update_person(person, data)

        # Download person's portrait
        if data.get("profile_path"):
            download_portrait(person, data.get("profile_path"), "w300")
            download_portrait(person, data.get("profile_path"), "w500")
        else:
            logging.warning(f"No profile_path found for person ID {person}")

        data["biography"] = ""  # to avoid logging large text
        if status:
            updated_persons += 1
            logging.info(f"Updated person successfully: {data}")
        else:
            logging.error(f"Failed to update person ID {person} with data {data}")

    message = f"Updated {updated_persons}/{number_of_persons} persons from {sys.argv[1]}. Took {round(time.time() - start_time, 2)} seconds"
    logging.info(message)
