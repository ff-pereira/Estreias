"""
    author: ffpereira
    date: 2025-11-21
"""

from apifairy import response
from sqlalchemy.orm import selectinload
from flask import Blueprint, abort, request
from datetime import datetime, date as dt_date
from apifairy.decorators import other_responses
from sqlalchemy import select, func, exists, asc, desc

from api import db
from api.utils import parse_bool, parse_int
from api.decorators import paginated_response
from api.models import Film, Screening, Genre, Country, Release, Cinema
from api.utils.details import get_details_filters, parse_details_filters
from api.schemas import FilmSchema, StringPaginationSchema, SimplifiedFilmSchema


films = Blueprint('films', __name__)

film_schema = FilmSchema()
simplified_film_schema = SimplifiedFilmSchema()


@films.route('/films', methods=['GET'])
@paginated_response(simplified_film_schema, pagination_schema=StringPaginationSchema)
@other_responses({400: 'Invalid filter parameters'})
def list_films():
    """List all films with comprehensive filtering, sorting, and pagination.

    Retrieves a paginated list of films with optional filtering by various
    movie criteria, sorting options, and support for release date filtering
    including Portuguese release dates.

    Query Parameters:
        sort (str): Sort field. Options: 'release_date', 'pt_release_date',
            'runtime', 'title', 'budget', 'revenue'. Default: 'pt_release_date'
        sort_dir (str): Sort direction. Options: 'asc', 'desc'. Default: 'asc'
        upcoming (bool): Filter to upcoming films (future Portuguese release dates)
        release_year (int): Filter by release year
        runtime (int): Filter by exact runtime in minutes
        cinemas (str): Comma-separated list of cinema IDs to filter films showing at
        pt_release_date (str): Filter by specific Portuguese release date (YYYY-MM-DD)
        in_cinemas (str): Filter films currently in cinemas
        title (str): Filter by film title (partial match)
        genres (str): Comma-separated list of genre IDs to filter by
        countries (str): Comma-separated list of country codes to filter by
        distributors (str): Comma-separated list of distributor names to filter by
        content_ratings (str): Comma-separated list of content ratings to filter by
        language (str): Filter by original language code

    Returns:
        PaginatedResponse: Paginated list of simplified film objects containing
            id, title, poster, url, release_year, runtime, and release_date.

    Raises:
        HTTPException: 400 if invalid sort field, sort direction, or date format.
    """
    sort = request.args.get('sort', 'pt_release_date')
    sort_dir = request.args.get('sort_dir', 'asc').lower()

    if sort_dir not in ("asc", "desc"):
        abort(400, description="Invalid sort_dir")

    filters = get_details_filters()
    upcoming = parse_bool(request.args.get('upcoming'))
    release_year = request.args.get('release_year')
    runtime = request.args.get('runtime')
    cinemas = request.args.get('cinemas')
    pt_release_date = request.args.get('pt_release_date')

    query = db.session.query(Film)

    query = query.options(
        selectinload(Film.genres),
        selectinload(Film.countries),
    )

    release_subq = (
        select(
            Release.film_id,
            func.min(Release.date).label("pt_release_date")
        )
        .where(Release.country_id == 'PT')
        .group_by(Release.film_id)
        .subquery()
    )

    sortable_fields = {
        "release_date": Film.release_date,
        "pt_release_date": release_subq.c.pt_release_date,
        "runtime": Film.runtime,
        "title": Film.title,
        "budget": Film.budget,
        "revenue": Film.revenue,
    }

    if sort not in sortable_fields:
        abort(400, description="Invalid sort field")

    column = sortable_fields[sort]

    if sort == "pt_release_date":
        query = query.join(
            release_subq,
            release_subq.c.film_id == Film.id
        )

    if sort_dir == "desc":
        query = query.order_by(desc(column), Film.id)
    else:
        query = query.order_by(asc(column), Film.id)

    if release_year:
        year = parse_int(release_year, "release_year")
        query = query.filter(func.extract('year', Film.release_date) == year)

    if runtime:
        runtime_value = parse_int(runtime, "runtime")
        query = query.filter(Film.runtime == runtime_value)

    cinema_ids = []
    if cinemas:
        cinema_ids = [c.strip() for c in cinemas.split(",") if c.strip()]

    if cinema_ids:
        query = query.filter(
            exists().where(
                (Screening.film_id == Film.id) &
                (Screening.cinema_id.in_(cinema_ids))
            )
        )

    if pt_release_date:
        try:
            parsed_date = datetime.strptime(pt_release_date, "%Y-%m-%d").date()
        except ValueError:
            abort(400, description="Invalid pt_release_date format (YYYY-MM-DD)")

        query = query.filter(
            exists().where(
                (Release.film_id == Film.id) &
                (Release.country_id == 'PT') &
                (Release.date == parsed_date)
            )
        )

    if upcoming:
        today = dt_date.today()
        query = query.filter(
            exists().where(
                (Release.film_id == Film.id) &
                (Release.country_id == 'PT') &
                (Release.date > today)
            )
        )

    query = parse_details_filters(query, **filters)

    return query


@films.route('/film/<film_id>', methods=['GET'])
@response(film_schema)
@other_responses({404: 'Film not found'})
def get_film(film_id):
    """Retrieve a complete film by its ID.

    Args:
        film_id (str): The unique identifier of the film to retrieve.

    Returns:
        dict: A dictionary containing complete film details including genres,
            countries, screenings, and release information.

    Raises:
        HTTPException: 404 if no film exists with the specified ID.
    """
    return db.session.get(Film, film_id) or abort(404)
