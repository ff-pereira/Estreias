"""
    author: ffpereira
    date: 2025-11-21
"""

from apifairy import response
from flask import Blueprint, abort
from apifairy.decorators import other_responses

from api import db
from api.schemas import LanguageSchema
from api.models import Film, Genre, Country, Language
from api.utils.details import get_details_filters, parse_details_filters

language_schema = LanguageSchema()
languages_schema = LanguageSchema(many=True)

languages = Blueprint('languages', __name__)


@languages.route('/languages', methods=['GET'])
@response(languages_schema)
@other_responses({400: 'Invalid filter parameters'})
def list_languages():
    """List all languages with optional filtering.

    Retrieves a list of languages that can be filtered by various movie-related
    criteria. The response includes language IDs and English names sorted
    alphabetically.

    Query Parameters:
        in_cinemas (str): Filter languages of movies currently in cinemas
        title (str): Filter languages of movies with matching title
        genres (str): Filter languages of movies belonging to specified genres
        countries (str): Filter languages of movies from specified countries
        distributors (str): Filter languages of movies distributed by specified distributors
        content_ratings (str): Filter languages of movies with specified content ratings
        language (str): Filter languages associated with movies that have this original language

    Returns:
        list: A list of language dictionaries containing 'id' and 'name' fields.

    Raises:
        HTTPException: 400 if filter parameters are invalid.
    """
    filters = get_details_filters()
    query = db.session.query(Language.id, Language.english_name.label("name")).order_by(Language.name.asc())
    query = parse_details_filters(query, **filters)

    return query.all()


@languages.route('/language/<language_id>', methods=['GET'])
@response(language_schema)
@other_responses({404: 'Language not found'})
def get_language(language_id):
    """Retrieve a single language by its ID.

    Args:
        language_id (str): The unique identifier of the language to retrieve.

    Returns:
        dict: A dictionary containing the language 'id' and 'name'.

    Raises:
        HTTPException: 404 if no language exists with the specified ID.
    """
    result = db.session.query(Language.id, Language.english_name.label("name")).filter(Language.id == language_id.lower()).first()

    if not result:
        abort(404)

    return {'id': result.id, 'name': result.name}
