"""
    author: ffpereira
    date: 2025-11-21
"""

from flask import Blueprint, abort
from apifairy.decorators import arguments
from datetime import datetime, date as dt_date, timedelta

from api import db
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from api.decorators import paginated_response
from api.models import Release, Screening, Film, Crew
from api.schemas import ReleaseSchema, DatePaginationSchema, ReleasesPaginationSchema

releases = Blueprint('releases', __name__)

releases_schema = ReleaseSchema(many=True)

OFFSET_DAYS_BACK = 5
MAX_RELEASE_LIMIT = 5
DEFAULT_RELEASE_LIMIT = 25


def build_release_query():
    """Build base query with eager loading for release relationships.

    Returns:
        SQLAlchemy query: Query with joinedload and selectinload options
            for film, language, countries, crew, and genres.
    """
    return (
        db.session.query(Release)
        .options(
            joinedload(Release.film).joinedload(Film.original_language_obj),
            joinedload(Release.film).selectinload(Film.countries),
            joinedload(Release.film).selectinload(Film.crew).joinedload(Crew.person),
            joinedload(Release.film).selectinload(Film.genres),
        )
    )


def parse_pagination_params(pagination):
    """Parse and validate pagination parameters from request.

    Args:
        pagination: Raw pagination parameters from request.

    Returns:
        tuple: (limit, offset, cinemas_list, after, before, title_search)
            - limit: Validated limit value (capped at MAX_RELEASE_LIMIT)
            - offset: Requested offset (may be None)
            - cinemas_list: List of cinema IDs to filter by
            - after: Datetime for filtering releases after this date
            - before: Datetime for filtering releases before this date
            - title_search: String to search in release titles

    Raises:
        BadRequest: If date format is invalid or after date is not before before date.
    """
    limit = min(pagination.get('limit', DEFAULT_RELEASE_LIMIT), MAX_RELEASE_LIMIT)
    offset = pagination.get('offset')
    cinemas = pagination.get("cinemas")
    cinemas_list = [c.strip() for c in cinemas.split(",")] if cinemas else []
    title_search = pagination.get("title_search")

    def parse_dt(field):
        val = pagination.get(field)
        if not val:
            return None
        try:
            return datetime.fromisoformat(val)
        except ValueError:
            abort(400, description=f"Invalid '{field}' datetime format. Use ISO 8601 format.")

    after, before = parse_dt('after'), parse_dt('before')
    if after and before and after >= before:
        abort(400, description="'after' must be earlier than 'before'.")

    return limit, offset, cinemas_list, after, before, title_search


def apply_filters(query, cinemas_list, after, before, title_search):
    """Apply all filters to the release query.

    Args:
        query: SQLAlchemy query object.
        cinemas_list: List of cinema IDs to filter by.
        after: Datetime for filtering releases after this date.
        before: Datetime for filtering releases before this date.
        title_search: String to search in release titles.

    Returns:
        SQLAlchemy query: Query with all filters applied.
    """
    if after:
        query = query.filter(Release.date >= after.date())

    if before:
        query = query.filter(Release.date < before.date())

    if title_search:
        pattern = f"%{title_search.strip().lower()}%"
        query = query.filter(func.lower(Release.title).like(pattern))

    if cinemas_list:
        query = query.join(Screening, Screening.film_id == Release.film_id)
        query = query.filter(Screening.cinema_id.in_(cinemas_list))
    return query


def get_offset_for_today(all_dates, offset=None):
    """Determine pagination offset, defaulting to today's position.

    Args:
        all_dates: Sorted list of all available release dates.
        offset: Requested offset (None to auto-calculate).

    Returns:
        int: Calculated offset index for pagination.
    """
    if offset is not None:
        return offset

    today = dt_date.today() - timedelta(days=OFFSET_DAYS_BACK)
    for i, d in enumerate(all_dates):
        if d >= today:
            return i
    return 0


def group_releases_by_date(releases_list):
    """Group releases by date after formatting each release.

    Args:
        releases_list: List of Release objects.

    Returns:
        dict: Dates mapped to lists of formatted release data.
    """
    grouped = {}
    for r in releases_list:
        film = r.film
        key = r.date.isoformat()

        directors = [
            {
                "id": crew.person.id,
                "name": crew.person.name,
            }
            for crew in film.crew
            if crew.role.lower() == "director"
        ]

        genres = [
            {
                "id": g.id,
                "name": g.name,
            }
            for g in film.genres
        ]

        grouped.setdefault(key, []).append({
            "film_id": r.film_id,
            "title": film.title,
            "poster": r.poster,
            "popularity": r.popularity,
            "imdb_id": film.imdb_id,
            "original_title": film.original_title,
            "portuguese_title": film.portuguese_title,
            "release_year": film.release_year,
            "runtime": film.runtime,
            "content_rating": film.content_rating,
            "distributor": film.distributor,
            "original_language": {
                "id": film.original_language_obj.id if film.original_language_obj else None,
                "name": film.original_language_obj.name if film.original_language_obj else None,
                "english_name": film.original_language_obj.english_name if film.original_language_obj else None,
            } if film.original_language_obj else None,
            "countries": [
                {
                    "id": c.id,
                    "name": c.name,
                    "flag": c.flag,
                }
                for c in film.countries
            ],
            "directors": directors,
            "genres": genres,
        })
    return grouped


def serialize_grouped_releases(grouped, page_dates):
    """Convert grouped releases into final paginated response format.

    Args:
        grouped: Dict of dates to formatted releases.
        page_dates: List of dates for the current page.

    Returns:
        list: Formatted response data with date, days_until, and releases.
    """
    data = [
        {
            "date": date.isoformat(),
            "days_until": (date - dt_date.today()).days,
            "releases": grouped.get(date.isoformat(), []),
        }
        for date in page_dates
    ]
    return data


@releases.route('/grouped_releases', methods=['GET'])
@arguments(ReleasesPaginationSchema)
def list_grouped_releases(pagination):
    """List releases grouped by date with pagination.

    Returns releases organized by date, starting at today or the next
    available release. Supports filtering by date range, title search,
    and cinema restrictions.

    Args:
        pagination: Pagination parameters including limit, offset,
            after, before, title_search, and cinemas.

    Returns:
        dict: Response with data and pagination metadata.
            - data: List of date groups with releases
            - pagination: Count, limit, offset, and total

    Raises:
        BadRequest: If any filter parameter is invalid.
    """
    limit, offset, cinemas_list, after, before, title_search = parse_pagination_params(pagination)

    query = build_release_query()
    query = apply_filters(query, cinemas_list, after, before, title_search)

    all_dates = [d[0] for d in query.with_entities(Release.date).distinct().order_by(Release.date).all()]
    total_dates = len(all_dates)

    offset = get_offset_for_today(all_dates, offset)
    page_dates = all_dates[offset:offset + limit]

    if not page_dates:
        return {
            "data": [],
            "pagination": {
                "count": 0,
                "limit": limit,
                "offset": offset,
                "total": total_dates
            }
        }

    filtered_releases = query.filter(Release.date.in_(page_dates)).order_by(Release.date, Release.popularity.desc()).all()
    grouped = group_releases_by_date(filtered_releases)
    data = serialize_grouped_releases(grouped, page_dates)

    return {
        "data": data,
        "pagination": {
            "count": len(data),
            "limit": limit,
            "offset": offset,
            "total": total_dates
        }
    }


@releases.route('/releases', methods=['GET'])
@paginated_response(releases_schema, order_by=Release.date,
                    order_direction='asc',
                    pagination_schema=DatePaginationSchema)
def list_releases():
    """List all releases with pagination.

    Returns a simple paginated list of all releases without grouping.
    Use this endpoint for raw release data or simple listings.

    Returns:
        SQLAlchemy query: Query for Release objects.
    """
    return db.session.query(Release)
