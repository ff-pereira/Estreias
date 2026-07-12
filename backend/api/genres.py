"""
    author: ffpereira
    date: 2025-11-21
"""

from sqlalchemy import func
from apifairy import response
from flask import Blueprint, abort
from apifairy.decorators import other_responses

from api import db
from api.models import Film, Genre
from api.schemas import GenreSchema, CountSchema
from api.utils.details import get_details_filters, parse_details_filters

genres = Blueprint('genres', __name__)

genre_schema = GenreSchema()
genres_counts_schema = CountSchema(many=True)


@genres.route('/genres', methods=['GET'])
@response(genres_counts_schema)
@other_responses({400: 'Invalid filter parameters'})
def list_genres():
    """List all genres with film counts and optional filtering.

    Retrieves a list of genres along with the count of films in each genre.
    Results can be filtered by various movie-related criteria and are sorted
    alphabetically by genre name.

    Query Parameters:
        in_cinemas (str): Filter genres of movies currently in cinemas
        title (str): Filter genres of movies with matching title
        genres (str): Filter genres of movies belonging to specified genres
        countries (str): Filter genres of movies from specified countries
        distributors (str): Filter genres of movies distributed by specified distributors
        content_ratings (str): Filter genres of movies with specified content ratings
        language (str): Filter genres of movies with this original language

    Returns:
        list: A list of genre dictionaries containing 'id', 'name', and 'film_count' fields.

    Raises:
        HTTPException: 400 if filter parameters are invalid.
    """
    filters = get_details_filters()

    query= (
        db.session.query(
            Genre.id, Genre.name,
            func.count(Film.id).label("film_count")
        )
        .join(Genre.films)
        .group_by(Genre.id)
        .order_by(Genre.name.asc())
    )
    query = parse_details_filters(query, **filters)

    return query.all()


@genres.route('/genre/<genre_id>', methods=['GET'])
@response(genre_schema)
@other_responses({404: 'Genre not found'})
def get_genre(genre_id):
    """Retrieve a single genre by its ID.

    Args:
        genre_id (str): The unique identifier of the genre to retrieve.

    Returns:
        dict: A dictionary containing the genre 'id' and 'name'.

    Raises:
        HTTPException: 404 if no genre exists with the specified ID.
    """
    result = db.session.query(Genre.id, Genre.name).filter(Genre.id == genre_id).first()

    if not result:
        abort(404)

    return {'id': result.id, 'name': result.name}
