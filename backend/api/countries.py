"""
    author: ffpereira
    date: 2025-11-21
"""

from sqlalchemy import func
from apifairy import response
from flask import Blueprint, abort, url_for
from apifairy.decorators import other_responses

from api import db
from api.models import Film, Country
from api.schemas import CountrySchema, CountSchema
from api.utils.details import get_details_filters, parse_details_filters

countries = Blueprint('countries', __name__)

country_schema = CountrySchema()
countries_counts_schema = CountSchema(many=True)


@countries.route('/countries', methods=['GET'])
@response(countries_counts_schema)
@other_responses({400: 'Invalid filter parameters'})
def list_countries():
    """List all countries with film counts and optional filtering.

    Retrieves a list of countries along with the count of films produced in
    each country. Results can be filtered by various movie-related criteria
    and are sorted alphabetically by country name.

    Query Parameters:
        in_cinemas (str): Filter countries of movies currently in cinemas
        title (str): Filter countries of movies with matching title
        genres (str): Filter countries of movies belonging to specified genres
        countries (str): Filter countries by country name
        distributors (str): Filter countries of movies distributed by specified distributors
        content_ratings (str): Filter countries of movies with specified content ratings
        language (str): Filter countries of movies with this original language

    Returns:
        list: A list of country dictionaries containing 'id', 'name', and 'film_count' fields.

    Raises:
        HTTPException: 400 if filter parameters are invalid.
    """
    filters = get_details_filters()

    query = (
        db.session.query(
            Country.id, Country.name,
            func.count(Film.id).label("film_count")
        )
        .join(Country.films)
        .group_by(Country.id)
        .order_by(Country.name.asc())
    )
    query = parse_details_filters(query, **filters)

    return query.all()


@countries.route('/country/<country_id>', methods=['GET'])
@response(country_schema)
@other_responses({404: 'Country not found'})
def get_country(country_id):
    """Retrieve a single country by its ID.

    Args:
        country_id (str): The unique identifier of the country to retrieve
            (case-insensitive, will be converted to uppercase).

    Returns:
        dict: A dictionary containing the country 'id', 'name', and 'flag' URL.

    Raises:
        HTTPException: 404 if no country exists with the specified ID.
    """
    result = db.session.query(Country.id, Country.name).filter(Country.id == country_id.upper()).first()

    if not result:
        abort(404)

    return {'id': result.id, 'name': result.name, 'flag': url_for('static', filename=f'flags/{result.id}.png', _external=True)}
