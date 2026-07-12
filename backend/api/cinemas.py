"""
    author: ffpereira
    date: 2025-11-21
"""

from apifairy import response
from datetime import date, timedelta
from sqlalchemy import func, select, or_
from flask import Blueprint, abort, request
from apifairy.decorators import other_responses

from api import db
from api.models import Film, Cinema, Country, Genre, Screening
from api.schemas import (CinemaSchema, CinemaWithCountSchema, CinemaNowShowingFilmSchema,
                         CitiesResponseSchema, RegionsResponseSchema, GroupsResponseSchema)

cinemas = Blueprint('cinemas', __name__)

cinema_schema = CinemaSchema()
cinemas_schema = CinemaSchema(many=True)
cities_schema = CitiesResponseSchema()
groups_schema = GroupsResponseSchema()
regions_schema = RegionsResponseSchema()
cinemas_counts_schema = CinemaWithCountSchema(many=True)
cinema_now_showing_film_schema = CinemaNowShowingFilmSchema(many=True)


@cinemas.route('/cinemas', methods=['GET'])
@response(cinemas_counts_schema)
def list_cinemas():
    """List all cinemas in Portugal with optional filtering.

    Retrieves a list of Portuguese cinemas with their group affiliations.
    Results can be filtered by various criteria and are sorted by region
    then by cinema name.

    Query Parameters:
        title (str): Filter cinemas by name (partial match, case-insensitive)
        cities (str): Comma-separated list of cities to filter by
        groups (str): Comma-separated list of cinema groups to filter by
        film_id (str): Filter cinemas currently showing a specific film

    Returns:
        list: A list of cinema dictionaries containing 'id', 'name', and 'group' fields.
    """
    name = request.args.get('name')
    cities = request.args.get('cities')
    groups = request.args.get('groups')
    film_id = request.args.get('film_id')

    query = db.session.query(
        Cinema.id,
        Cinema.name,
        Cinema.group
    ).filter(Cinema.country_id == 'PT').order_by(Cinema.address_region.asc(), Cinema.name.asc())

    # Only join Screening and Film if filtering by film_id
    if film_id:
        today = date.today()
        query = query.join(Screening).join(Film).filter(
            Film.id == film_id,
            or_(Screening.last_seen.is_(None), Screening.last_seen == today)
        )

    if name:
        query = query.filter(Cinema.name.ilike(f'%{name}%'))

    if cities:
        city_list = [c.strip() for c in cities.split(',') if c.strip()]
        if city_list:
            query = query.filter(Cinema.address_region.in_(city_list))

    if groups:
        group_list = [g.strip() for g in groups.split(',') if g.strip()]
        if group_list:
            query = query.filter(Cinema.group.in_(group_list))

    return query.all()


@cinemas.route('/cinema/<cinema_id>', methods=['GET'])
@response(cinema_schema)
@other_responses({404: 'Cinema not found'})
def get_cinema(cinema_id):
    """Retrieve a single cinema by its ID.

    Args:
        cinema_id (str): The unique identifier of the cinema to retrieve.

    Returns:
        dict: A dictionary containing the cinema details.

    Raises:
        HTTPException: 404 if no cinema exists with the specified ID.
    """
    return db.session.get(Cinema, cinema_id) or abort(404)


@cinemas.route('/cinema/<cinema_id>/now_showing', methods=['GET'])
@response(cinema_now_showing_film_schema)
def get_cinema_now_showing(cinema_id):
    """Retrieve films currently showing in a specific cinema.

    Args:
        cinema_id (str): The unique identifier of the cinema.

    Returns:
        list: A list of film dictionaries containing id, title, poster, url,
            runtime, release_year, first_seen, and last_seen fields.
    """
    yesterday = date.today() - timedelta(days=1)

    stmt = (
        select(Film, Screening.first_seen, Screening.last_seen)
        .join(Screening)
        .where(
            Screening.cinema_id == cinema_id,
            or_(
                Screening.last_seen.is_(None),
                Screening.last_seen >= yesterday
            )
        )
        .order_by(Screening.first_seen.desc())
    )

    results = db.session.execute(stmt).all()

    films = []
    for film, first_seen, last_seen in results:
        films.append({
            "id": film.id,
            "title": film.title,
            "poster": film.poster,
            "url": film.url,
            "runtime": film.runtime,
            "release_year": film.release_year,
            "first_seen": first_seen if first_seen else None,
            "last_seen": last_seen if last_seen else None
        })

    return films


@cinemas.route('/cities', methods=['GET'])
@response(cities_schema)
def list_cities():
    """List all cities in Portugal that have cinemas.

    Returns:
        dict: A dictionary containing a 'data' key with a list of city
            dictionaries containing 'id' and 'name' fields, sorted alphabetically.
    """
    cities = db.session.query(Cinema.address_region).distinct().filter(
        Cinema.country_id == 'PT',
        Cinema.address_region.isnot(None)
    ).order_by(Cinema.address_region.asc()).all()
    city_list = [{"id": city, "name": city} for (city,) in cities]
    return {'data': city_list}


@cinemas.route('/portugal_regions', methods=['GET'])
@response(regions_schema)
def get_portuguese_regions():
    """List Portuguese regions with cinema counts and optional filtering.

    Retrieves a list of Portuguese regions along with the count of cinemas
    in each region. Results can be filtered by various criteria.

    Query Parameters:
        cities (str): Comma-separated list of cities to filter by
        groups (str): Comma-separated list of cinema groups to filter by
        film_id (str): Filter regions with cinemas currently showing a specific film

    Returns:
        dict: A dictionary containing a 'data' key with a list of region
            dictionaries containing 'id', 'name', and 'count' fields.
    """
    cities = request.args.get('cities')
    groups = request.args.get('groups')
    film_id = request.args.get('film_id')

    query = (
        db.session.query(
            Cinema.address_region,
            func.count(Cinema.id)
        )
        .filter(Cinema.country_id == 'PT', Cinema.address_region.isnot(None))
        .group_by(Cinema.address_region)
        .order_by(Cinema.address_region)
    )

    if film_id:
        today = date.today()
        query = query.join(Screening).filter(
            Screening.film_id == film_id,
            or_(Screening.last_seen.is_(None), Screening.last_seen == today),
            Cinema.country_id == 'PT'
        )

    if cities:
        city_list = [c.strip() for c in cities.split(',') if c.strip()]
        if city_list:
            query = query.filter(Cinema.address_region.in_(city_list))

    if groups:
        group_list = [g.strip() for g in groups.split(',') if g.strip()]
        if group_list:
            query = query.filter(Cinema.group.in_(group_list))

    cinemas_by_region = query.all()

    cinemas_by_region_list = [
        {
            "id": region,
            "name": region,
            "count": count
        }
        for region, count in cinemas_by_region
    ]

    return {'data': cinemas_by_region_list}


@cinemas.route('/cinema_groups', methods=['GET'])
@response(groups_schema)
def list_cinema_groups():
    """List all cinema groups operating in Portugal.

    Returns:
        dict: A dictionary containing a 'data' key with a list of cinema group
            dictionaries containing 'id' and 'name' fields, sorted alphabetically.
    """
    groups = db.session.query(Cinema.group).distinct().filter(
        Cinema.country_id == 'PT',
        Cinema.group.isnot(None)
    ).order_by(Cinema.group.asc()).all()
    group_list = [{"id": group, "name": group} for (group,) in groups]
    return {'data': group_list}
