"""
    author: ffpereira
    date: 2025-11-21
"""

from sqlalchemy import func
from flask import Blueprint, request
from apifairy import response, other_responses

from api import db
from api.models import Film
from api.schemas import CountSchema
from api.utils.details import get_details_filters, parse_details_filters

content_ratings = Blueprint('content_ratings', __name__)

content_ratings_count_schema = CountSchema(many=True)

@content_ratings.route('/content_ratings', methods=['GET'])
@response(content_ratings_count_schema)
@other_responses({400: 'Invalid filter parameters'})
def list_content_ratings():
    """List all content ratings with film counts and optional filtering.

    Retrieves a list of content ratings along with the count of films bearing
    each rating. Results can be filtered by various movie-related criteria and
    are sorted by film count in descending order.

    Query Parameters:
        in_cinemas (str): Filter content ratings of movies currently in cinemas
        title (str): Filter content ratings of movies with matching title
        genres (str): Filter content ratings of movies belonging to specified genres
        countries (str): Filter content ratings of movies from specified countries
        distributors (str): Filter content ratings of movies distributed by specified distributors
        content_ratings (str): Filter content ratings by rating name
        language (str): Filter content ratings of movies with this original language

    Returns:
        list: A list of content rating dictionaries containing 'id', 'name', and 'film_count' fields.

    Raises:
        HTTPException: 400 if filter parameters are invalid.
    """

    filters = get_details_filters()

    query = (
        db.session.query(
            Film.content_rating.label('id'),
            Film.content_rating.label('name'),
            func.count(Film.id).label('film_count')
        )
        .filter(Film.content_rating.isnot(None))
    )
    query = parse_details_filters(query, **filters)
    query = query.group_by(Film.content_rating).order_by(func.count(Film.id).desc(), Film.content_rating.asc())

    return query.all()