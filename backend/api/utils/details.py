"""
    author: ffpereira
    date: 2025-11-21
"""

from flask import abort, request
from api.models import Film, Genre, Country


def get_details_filters():
    """Extracts and returns filter parameters from the Flask request object.

    Retrieves various filter parameters from the request's query string arguments
    and returns them as a dictionary. This function serves as a centralized way
    to collect all available filtering criteria for film queries.

    Returns:
        dict: A dictionary containing the filter keys
    """
    return {
        "in_cinemas": request.args.get('in_cinemas'),
        "title": request.args.get('title'),
        "genres": request.args.get('genres'),
        "countries": request.args.get('countries'),
        "distributor": request.args.get('distributors'),
        "content_rating": request.args.get('content_ratings').replace("-", "/") if request.args.get('content_ratings') else None,
        "original_language": request.args.get('language'),
    }


def parse_details_filters(query, in_cinemas, title, genres, countries, distributor, content_rating, original_language):
    """Applies filter conditions to a Film query based on provided parameters.

    This function dynamically builds an SQLAlchemy query for Film objects by
    applying various filter conditions. Each filter parameter is optional and
    only applied when provided. The function handles parameter parsing, type
    conversion, and validation.

    Args:
        query: SQLAlchemy query object for Film model to be filtered
        in_cinemas (str, optional): String indicating whether to filter by
            cinema availability. Accepts 'true'/'false', '1'/'0', or 'yes'/'no'.
            Invalid values trigger a 400 abort.
        title (str, optional): Title substring to search for (case-insensitive,
            partial match)
        genres (str, optional): Comma-separated list of genre IDs to filter by
        countries (str, optional): Comma-separated list of country codes to
            filter by (case-insensitive)
        distributor (str, optional): Comma-separated list of distributor names
            to filter by
        content_rating (str, optional): Comma-separated list of content ratings
            to filter by
        original_language (str, optional): Original language code to filter by
            (case-insensitive)

    Returns:
        SQLAlchemy query: The filtered query object with all applicable
            conditions applied

    Raises:
        400: If in_cinemas parameter contains an invalid value that cannot be
            parsed to boolean
    """
    if in_cinemas is not None:
        if in_cinemas.lower() in ['true', '1', 'yes']:
            in_cinemas = True
        elif in_cinemas.lower() in ['false', '0', 'no']:
            in_cinemas = False
        else:
            abort(400)

        query = query.filter(Film.in_cinemas == in_cinemas)

    if title:
        query = query.filter(Film.title.ilike(f'%{title}%'))

    if genres:
        genre_ids = [int(g.strip()) for g in genres.split(',') if g.strip().isdigit()]
        if genre_ids:
            query = query.filter(Film.genres.any(Genre.id.in_(genre_ids)))

    if countries:
        countries_ids = [c.strip().upper() for c in countries.split(',') if c.strip()]
        if countries_ids:
            query = query.filter(Film.countries.any(Country.id.in_(countries_ids)))

    if distributor:
        distributors = [d.strip() for d in distributor.split(',') if d.strip()]
        if distributors:
            query = query.filter(Film.distributor.in_(distributors))

    if content_rating:
        content_ratings = [cr.strip() for cr in content_rating.split(',') if cr.strip()]
        if content_ratings:
            query = query.filter(Film.content_rating.in_(content_ratings))

    if original_language:
        query = query.filter(Film.original_language == original_language.lower())

    return query
