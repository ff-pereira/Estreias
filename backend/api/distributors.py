"""
    author: ffpereira
    date: 2025-11-21
"""

from sqlalchemy import func
from apifairy import response
from flask import Blueprint, abort
from apifairy.decorators import other_responses

from api import db
from api.models import Film
from api.schemas import DistributorSchema, CountSchema
from api.utils.details import get_details_filters, parse_details_filters

distributors = Blueprint('distributors', __name__)

distributor_schema = DistributorSchema()
distributors_counts_schema = CountSchema(many=True)


@distributors.route('/distributors', methods=['GET'])
@response(distributors_counts_schema)
@other_responses({400: 'Invalid filter parameters'})
def list_distributors():
    """List all distributors with film counts and optional filtering.

    Retrieves a list of distributors along with the count of films distributed
    by each. Results can be filtered by various movie-related criteria and are
    sorted by film count in descending order.

    Query Parameters:
        in_cinemas (str): Filter distributors of movies currently in cinemas
        title (str): Filter distributors of movies with matching title
        genres (str): Filter distributors of movies belonging to specified genres
        countries (str): Filter distributors of movies from specified countries
        distributors (str): Filter distributors by distributor name
        content_ratings (str): Filter distributors of movies with specified content ratings
        language (str): Filter distributors of movies with this original language

    Returns:
        list: A list of distributor dictionaries containing 'id', 'name', and 'film_count' fields.

    Raises:
        HTTPException: 400 if filter parameters are invalid.
    """
    filters = get_details_filters()

    query = (
        db.session.query(
            Film.distributor.label('id'),
            Film.distributor.label('name'),
            func.count(Film.id).label('film_count')
        )
        .filter(Film.distributor.isnot(None))
    )
    query = parse_details_filters(query, **filters)
    query = query.group_by(Film.distributor).order_by(func.count(Film.id).desc(), Film.distributor.asc())

    return query.all()


@distributors.route('/distributor/<distributor_id>', methods=['GET'])
@response(distributor_schema)
@other_responses({404: 'Distributor not found'})
def get_distributor(distributor_id):
    """Retrieve a single distributor by its ID.

    Args:
        distributor_id (str): The unique identifier of the distributor to retrieve.

    Returns:
        dict: A dictionary containing the distributor 'id' and 'name'.

    Raises:
        HTTPException: 404 if no distributor exists with the specified ID.
    """
    result = db.session.query(Film.distributor.label('id')).filter(Film.distributor == distributor_id).first()

    if not result:
        abort(404)

    return {'id': result.id, 'name': result.id}
