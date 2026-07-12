"""
    author: ffpereira
    date: 2025-11-21
"""

from flask import Blueprint, abort, request, url_for
from sqlalchemy import select, func, case, desc, distinct, extract

from api import db
from datetime import date
from api.utils import safe_avg, safe_percentage
from api.models import Film, Genre, Country, film_countries, film_genres, Crew, Cast, Person, Release, Screening, Language

stats = Blueprint('stats', __name__)

GENRE_ANIMATION = 16
GENRE_DOCUMENTARY = 99

GENDER_MALE = 1
GENDER_FEMALE = 2
GENDERS = [GENDER_FEMALE, GENDER_MALE]

TOP_PERSONS_LIMIT = 5
TOP_POPULAR_LIMIT = 12
TOP_LANGUAGES_LIMIT = 10
TOP_DISTRIBUTORS_LIMIT = 5


def apply_runtime_filter(query, runtime_filter):
    """Apply runtime filter with validation."""
    try:
        if '-' in runtime_filter:
            min_r, max_r = runtime_filter.split('-')
            return query.filter(Film.runtime.between(int(min_r), int(max_r)))
        elif runtime_filter.startswith('>'):
            return query.filter(Film.runtime > int(runtime_filter[1:]))
        elif runtime_filter.startswith('<'):
            return query.filter(
                Film.runtime < int(runtime_filter[1:]),
                Film.runtime > 0
            )
        else:
            return query.filter(Film.runtime == int(runtime_filter))
    except ValueError:
        abort(400, description=f"Invalid runtime format: {runtime_filter}")


def apply_film_filters(query, args):
    """Apply all requested filters to a film query.

    Filters are applied sequentially from the args dictionary. Invalid
    filter values will trigger a 400 Bad Request response.

    Args:
        query: SQLAlchemy query object (typically Film.id query).
        args (dict): Filter parameters from request.args.

    Returns:
        SQLAlchemy query with all valid filters applied.

    Raises:
        BadRequest: If any filter value is invalid.
    """
    if args.get("language"):
        query = query.filter(Film.original_language == args["language"])

    if args.get("release_year"):
        try:
            year = int(args["release_year"])
            query = query.filter(Film.release_year == year)
        except ValueError:
            abort(400, description=f"Invalid release_year: {args['release_year']}")

    if args.get("pt_release_year"):
        try:
            year = int(args["pt_release_year"])
            query = query.join(Release).filter(extract('year', Release.date) == year)
        except ValueError:
            abort(400, description=f"Invalid pt_release_year: {args['pt_release_year']}")

    if args.get("month"):
        try:
            month = int(args["month"])
            if not 1 <= month <= 12:
                abort(400, description="Month must be between 1 and 12")
            query = query.join(Release).filter(extract('month', Release.date) == month)
        except ValueError:
            abort(400, description=f"Invalid month: {args['month']}")

    if args.get("runtime"):
        query = apply_runtime_filter(query, args["runtime"])

    if args.get("genre"):
        if not args["genre"].isdigit():
            abort(400, description=f"Invalid genre ID: {args['genre']}")
        query = query.join(film_genres).filter(film_genres.c.genre_id == int(args["genre"]))

    if args.get("country"):
        query = query.join(film_countries).filter(film_countries.c.country_id == args["country"])

    if args.get("distributor"):
        query = query.filter(Film.distributor == args["distributor"])

    if args.get("content_rating"):
        content_rating = args["content_rating"]
        if '-' in content_rating:
            content_rating = content_rating.replace('-', '/')
        else:
            return abort(400)
        query = query.filter(Film.content_rating == content_rating)

    if args.get("cinema"):
        cinema_id = args["cinema"]
        query = query.join(Film.screenings).filter(Screening.cinema_id == cinema_id)

    return query


def get_basic_stats(base_films, total_films):
    """Calculate basic aggregate statistics for films.

    Args:
        base_films: SQLAlchemy subquery of filtered film IDs.
        total_films (int): Total count of films after filtering.

    Returns:
        dict: Totals for genres, countries, languages, distributors,
              and animation/documentary counts with percentages.
    """
    total_genres = (
        db.session.query(func.count(distinct(film_genres.c.genre_id)))
        .join(base_films, film_genres.c.film_id == base_films.c.id)
        .scalar()
    )
    total_countries = (
        db.session.query(func.count(distinct(film_countries.c.country_id)))
        .join(base_films, film_countries.c.film_id == base_films.c.id)
        .scalar()
    )
    total_languages = (
        db.session.query(func.count(distinct(Film.original_language)))
        .join(base_films, Film.id == base_films.c.id)
        .filter(Film.original_language.isnot(None), Film.original_language != '')
        .scalar()
    )
    total_distributors = (
        db.session.query(func.count(distinct(Film.distributor)))
        .join(base_films, Film.id == base_films.c.id)
        .filter(Film.distributor.isnot(None))
        .scalar()
    )
    total_animation_films = (
        db.session.query(func.count(distinct(film_genres.c.film_id)))
        .join(base_films, film_genres.c.film_id == base_films.c.id)
        .filter(film_genres.c.genre_id == GENRE_ANIMATION)
        .scalar()
    )
    total_documentary_films = (
        db.session.query(func.count(distinct(film_genres.c.film_id)))
        .join(base_films, film_genres.c.film_id == base_films.c.id)
        .filter(film_genres.c.genre_id == GENRE_DOCUMENTARY)
        .scalar()
    )

    return {
        "genres": total_genres,
        "countries": total_countries,
        "languages": total_languages,
        "distributors": total_distributors,
        "animation_films": total_animation_films,
        "documentary_films": total_documentary_films,
        "percentage_documentary_films": safe_percentage(total_documentary_films, total_films),
        "percentage_animation_films": safe_percentage(total_animation_films, total_films),
    }


def get_releases(base_films):
    """Calculate release-related statistics.

    Args:
        base_films: SQLAlchemy subquery of filtered film IDs.

    Returns:
        dict: Release counts including upcoming, released, and
              Portugal-related films.
    """
    upcoming_releases = (
        db.session.query(func.count(distinct(Release.film_id)))
        .join(base_films, Release.film_id == base_films.c.id)
        .filter(Release.date >= date.today())
        .scalar()
    )
    released = (
        db.session.query(func.count(distinct(Release.film_id)))
        .join(base_films, Release.film_id == base_films.c.id)
        .filter(Release.date < date.today())
        .scalar()
    )
    pt_films = db.session.execute(
        select(
            func.count(distinct(film_countries.c.film_id))
            .filter(film_countries.c.country_id == 'PT')
            .label("with_portugal"),
            func.count(distinct(film_countries.c.film_id))
            .filter(
                film_countries.c.country_id == 'PT',
                ~film_countries.c.film_id.in_(
                    select(film_countries.c.film_id)
                    .join(base_films, film_countries.c.film_id == base_films.c.id)
                    .where(film_countries.c.country_id != 'PT')
                )
            )
            .label("only_portugal")
        )
        .join(base_films, film_countries.c.film_id == base_films.c.id)
    )
    with_portugal, only_portugal = pt_films.one()

    return {
        "upcoming": upcoming_releases,
        "released": released,
        "with_portugal": with_portugal,
        "only_portugal": only_portugal,
    }


def get_persons_stats(base_films):
    """Calculate comprehensive statistics about cast and crew.

    Computes totals by role, analyzes frequency distributions,
    and calculates various percentages and averages.

    Args:
        base_films: SQLAlchemy subquery of filtered film IDs.

    Returns:
        dict: Person statistics including:
            - actor/director/writer/composer/cinematographer counts
            - female-directed film counts
            - one-film vs multiple-film analysis
            - performance and credit statistics with percentages
    """
    total_actors = (
        db.session.query(func.count(distinct(Cast.person_id)))
        .join(base_films, Cast.film_id == base_films.c.id)
        .scalar()
    )
    total_directors = (
        db.session.query(func.count(distinct(Crew.person_id)))
        .join(base_films, Crew.film_id == base_films.c.id)
        .filter(Crew.role.ilike('director'))
        .scalar()
    )
    total_writers = (
        db.session.query(func.count(distinct(Crew.person_id)))
        .join(base_films, Crew.film_id == base_films.c.id)
        .filter(Crew.role.ilike('writer'))
        .scalar()
    )
    total_composers = (
        db.session.query(func.count(distinct(Crew.person_id)))
        .join(base_films, Crew.film_id == base_films.c.id)
        .filter(Crew.role.ilike('composer'))
        .scalar()
    )
    total_cinematographers = (
        db.session.query(func.count(distinct(Crew.person_id)))
        .join(base_films, Crew.film_id == base_films.c.id)
        .filter(Crew.role.ilike('cinematographer'))
        .scalar()
    )

    directors_with_one_film = (
        db.session.query(func.count())
        .select_from(
            db.session.query(Crew.person_id)
            .join(base_films, Crew.film_id == base_films.c.id)
            .filter(Crew.role.ilike('director'))
            .group_by(Crew.person_id)
            .having(func.count(distinct(Crew.film_id)) == 1)
            .subquery()
        )
        .scalar()
    )
    actors_with_one_film = (
        db.session.query(func.count())
        .select_from(
            db.session.query(Cast.person_id)
            .join(base_films, Cast.film_id == base_films.c.id)
            .group_by(Cast.person_id)
            .having(func.count(distinct(Cast.film_id)) == 1)
            .subquery()
        )
        .scalar()
    )
    actor_performance_stats = (
        db.session.query(
            func.count(Cast.film_id).label("total"),
            func.count(
                case(
                    (Cast.character.ilike('%(uncredited)%'), 1)
                )
            ).label("uncredited"),
            func.count(
                case(
                    (Cast.character.ilike('%(voice)%'), 1)
                )
            ).label("voice")
        )
        .join(base_films, Cast.film_id == base_films.c.id)
        .one()
    )

    total_actor_performances = actor_performance_stats.total
    uncredited_performances = actor_performance_stats.uncredited
    voice_performances = actor_performance_stats.voice

    total_director_credits = (
        db.session.query(func.count(Crew.film_id))
        .join(base_films, Crew.film_id == base_films.c.id)
        .filter(Crew.role.ilike('director'))
        .scalar()
    )

    total_female_directed = (
        db.session.query(func.count(distinct(Crew.film_id)))
        .join(Person, Crew.person_id == Person.id)
        .join(base_films, Crew.film_id == base_films.c.id)
        .filter(Crew.role.ilike('director'))
        .filter(Person.gender == GENDER_FEMALE)
        .scalar()
    )

    return {
        "actors": total_actors,
        "directors": total_directors,
        "writers": total_writers,
        "composers": total_composers,
        "cinematographers": total_cinematographers,
        "female_directed": total_female_directed,
        "percentage_female_directed": safe_percentage(total_female_directed, total_directors),
        "actors_with_one_film": actors_with_one_film,
        "actor_performances": total_actor_performances,
        "actors_with_multiple_films": total_actors - actors_with_one_film,
        "directors_with_one_film": directors_with_one_film,
        "percentage_directors_with_one_film": safe_percentage(directors_with_one_film, total_directors),
        "directors_with_multiple_films": total_directors - directors_with_one_film,
        "avg_credits_per_director": safe_avg(total_director_credits, total_directors),
        "avg_performances_per_actor": safe_avg(total_actor_performances, total_actors),
        "percentage_directors_with_multiple_films": safe_percentage((total_directors - directors_with_one_film),total_directors),
        "percentage_actors_with_one_film": safe_percentage(actors_with_one_film, total_actors),
        "percentage_actors_with_multiple_films": safe_percentage((total_actors - actors_with_one_film), total_actors),
        "uncredited_performances": uncredited_performances,
        "voice_performances": voice_performances,
        "director_credits": total_director_credits,
        "percentage_uncredited_performances": safe_percentage(uncredited_performances, total_actor_performances),
        "percentage_voice_performances": safe_percentage(voice_performances, total_actor_performances),
    }


def get_top_persons_by_role(base_films, limit=5):
    """Get top actors and crew members by gender for each role.

    Finds the most frequent collaborators across filtered films.
    Actors are counted by film appearances, crew by credits.

    Args:
        base_films: SQLAlchemy subquery of filtered film IDs.
        limit (int): Maximum number of people to return per category.
            Defaults to 5.

    Returns:
        tuple: (actors_by_gender, crew_by_gender)
            - actors_by_gender (dict): {gender_id: [person_data, ...]}
            - crew_by_gender (dict): {role: {gender_id: [person_data, ...]}}
            Each person_data contains: id, name, portrait, films_count
    """
    top_actors_by_gender = {}
    for g in GENDERS:
        top_actors = (
            db.session.query(
                Person.id, Person.name,
                func.count(Cast.film_id).label("films_count")
            )
            .join(Cast, Cast.person_id == Person.id)
            .join(base_films, Cast.film_id == base_films.c.id)
            .filter(Person.gender == g)
            .group_by(Person.id)
            .order_by(desc("films_count"))
            .limit(limit)
            .all()
        )

        top_actors_by_gender[str(g)] = [
            {
                "id": i,
                "name": n,
                "portrait": url_for('static', filename=f"images/persons/w300/{i}.jpg", _external=True),
                "films_count": c
            }
            for i, n, c in top_actors
        ]

    top_crew_by_gender = {}
    roles = [r[0] for r in db.session.query(Crew.role).filter(Crew.role.isnot(None)).distinct().all()]

    for role in roles:
        top_crew_by_gender[role.lower()] = {}

        for g in GENDERS:
            top_people = (
                db.session.query(
                    Person.id, Person.name,
                    func.count(Crew.film_id).label("films_count")
                )
                .join(Crew, Crew.person_id == Person.id)
                .join(base_films, Crew.film_id == base_films.c.id)
                .filter(Crew.role.ilike(role))
                .filter(Person.gender == g)
                .group_by(Person.id)
                .order_by(desc("films_count"))
                .limit(limit)
                .all()
            )

            top_crew_by_gender[role.lower()][str(g)] = [
                {
                    "id": i,
                    "name": n,
                    "portrait": url_for('static', filename=f"images/persons/w300/{i}.jpg", _external=True),
                    "films_count": c
                }
                for i, n, c in top_people
            ]
    return top_actors_by_gender, top_crew_by_gender


def get_popular_films(base_films):
    """Get the most popular films based on release popularity scores.

    Args:
        base_films: SQLAlchemy subquery of filtered film IDs.

    Returns:
        list: Top popular films with id, title, popularity, and poster URL.
    """
    top_popular_rows = (
        db.session.query(Film.id, Film.title, Release.popularity)
        .join(base_films, Film.id == base_films.c.id)
        .join(Release, Release.film_id == base_films.c.id)
        .filter(Release.popularity.isnot(None))
        .order_by(desc(Release.popularity))
        .limit(TOP_POPULAR_LIMIT)
        .all()
    )

    top_popular_films = [
        {"id": film_id, "title": title, "popularity": popularity,
         "poster": url_for('static', filename=f"images/posters/original/{film_id}.jpg", _external=True)
         }
        for film_id, title, popularity in top_popular_rows
    ]
    return top_popular_films


def get_runtime_stats(base_films):
    """Group films by runtime ranges (e.g., 70-79, 80-89 minutes).

    Args:
        base_films: SQLAlchemy subquery of filtered film IDs.

    Returns:
        list: Runtime distribution with each entry containing:
            runtime_range, count, avg_runtime
    """
    runtime_bins = [
        (0, "<70", Film.runtime < 70),
        (1, "70-79", Film.runtime.between(70, 79)),
        (2, "80-89", Film.runtime.between(80, 89)),
        (3, "90-99", Film.runtime.between(90, 99)),
        (4, "100-109", Film.runtime.between(100, 109)),
        (5, "110-119", Film.runtime.between(110, 119)),
        (6, "120-129", Film.runtime.between(120, 129)),
        (7, "130-139", Film.runtime.between(130, 139)),
        (8, "140-149", Film.runtime.between(140, 149)),
        (9, "150-159", Film.runtime.between(150, 159)),
        (10, "160-169", Film.runtime.between(160, 169)),
        (11, "170-180", Film.runtime.between(170, 180)),
        (12, ">180", Film.runtime > 180),
    ]

    runtime_case = case(
        {cond: label for _, label, cond in runtime_bins},
        else_="Unknown"
    )
    order_case = case(
        {cond: idx for idx, _, cond in runtime_bins},
        else_=99
    )

    films_by_runtime = (
        db.session.query(
            runtime_case.label("runtime_range"),
            func.count(Film.id).label("count"),
            func.avg(func.nullif(Film.runtime, 0)).label("avg_runtime"),
            order_case.label("sort_order")
        )
        .join(base_films, Film.id == base_films.c.id)
        .filter(Film.runtime > 0)
        .group_by("runtime_range", "sort_order")
        .order_by("sort_order")
        .all()
    )

    films_by_runtime_list = [
        {"runtime_range": r, "count": c, "avg_runtime": round(ar, 2) if ar else None}
        for r, c, ar, _ in films_by_runtime
    ]
    return films_by_runtime_list


def get_films_by_attributes(base_films):
    """Group films by rating, genre, language, and distributor.

    Args:
        base_films: SQLAlchemy subquery of filtered film IDs.

    Returns:
        dict: Grouped statistics with keys:
            - films_by_content_rating
            - films_by_country
            - films_by_genre
            - films_by_language
            - films_by_distributor
    """
    def format_stats(results, key_name):
        return [
            {key_name: k, "count": c, "avg_runtime": round(ar, 2) if ar else None}
            for k, c, ar in results
        ]

    films_by_content_rating = (
        db.session.query(
            Film.content_rating.label("content_rating"),
            func.count(Film.id).label("count"),
            func.avg(func.nullif(Film.runtime, 0)).label("avg_runtime")
        )
        .join(base_films, Film.id == base_films.c.id)
        .filter(Film.content_rating.isnot(None), Film.content_rating != '')
        .group_by(Film.content_rating)
        .order_by(Film.content_rating)
        .all()
    )

    films_by_content_rating_list = format_stats(films_by_content_rating, "content_rating")

    films_by_country = (
        db.session.query(
            Country.id,
            Country.name,
            func.coalesce(func.count(distinct(base_films.c.id)), 0).label("count"),
        )
        .outerjoin(film_countries, film_countries.c.country_id == Country.id)
        .outerjoin(base_films, film_countries.c.film_id == base_films.c.id)
        .group_by(Country.id, Country.name)
        .order_by(desc("count"))
        .all()
    )

    films_by_country_list = [
        {
            "country_id": cid,
            "flag_url": url_for('static', filename=f"flags/{cid.lower()}.png", _external=True),
            "country_name": name,
            "count": c,
            # "avg_runtime": round(ar, 2) if ar else None
        }
        for cid, name, c in films_by_country
    ]

    films_by_genre = (
        db.session.query(
            Genre.id.label("genre_id"),
            Genre.name.label("genre_name"),
            func.count(distinct(film_genres.c.film_id)).label("count"),
            func.avg(func.nullif(Film.runtime, 0)).label("avg_runtime")
        )
        .join(film_genres, film_genres.c.genre_id == Genre.id)
        .join(base_films, film_genres.c.film_id == base_films.c.id)
        .join(Film, Film.id == base_films.c.id)
        .group_by(Genre.id, Genre.name)
        .order_by(Genre.name)
        .all()
    )

    films_by_genre_list = [
        {"genre_id": gid, "genre_name": name, "count": c, "avg_runtime": round(ar, 2) if ar else None}
        for gid, name, c, ar in films_by_genre
    ]

    films_by_language = (
        db.session.query(
            Language.id.label("language_id"),
            Language.english_name.label("language"),
            func.count(Film.id).label("count"),
            func.avg(func.nullif(Film.runtime, 0)).label("avg_runtime"),
        )
        .join(base_films, Film.id == base_films.c.id)
        .join(Language, Film.original_language == Language.id)
        .filter(Film.original_language.isnot(None), Film.original_language != '')
        .group_by(Language.english_name, Language.id)
        .order_by(func.count(Film.id).desc(), Language.english_name)
        .limit(TOP_LANGUAGES_LIMIT)
        .all()
    )
    films_by_language_list =  [
        {"language_id": i, "language": k, "count": c, "avg_runtime": round(ar, 2) if ar else None}
        for i, k, c, ar in films_by_language
    ]

    films_by_distributor = (
        db.session.query(
            Film.distributor.label("distributor"),
            func.count(Film.id).label("count"),
            func.avg(func.nullif(Film.runtime, 0)).label("avg_runtime")
        )
        .join(base_films, Film.id == base_films.c.id)
        .filter(Film.distributor.isnot(None), Film.distributor != '')
        .group_by(Film.distributor)
        .order_by(func.count(Film.id).desc())
        .limit(TOP_DISTRIBUTORS_LIMIT)
        .all()
    )
    films_by_distributor_list = format_stats(films_by_distributor, "distributor")

    return {
        "films_by_content_rating": films_by_content_rating_list,
        "films_by_country": films_by_country_list,
        "films_by_genre": films_by_genre_list,
        "films_by_language": films_by_language_list,
        "films_by_distributor": films_by_distributor_list,
    }


def get_grouped_releases(base_films):
    """Group release data by year and month.

    Args:
        base_films: SQLAlchemy subquery of filtered film IDs.

    Returns:
        dict: Releases grouped by year, month, and films by release year.
    """
    releases_by_year = (
        db.session.query(
            extract('year', Release.date).label('year'),
            func.count(Release.film_id).label('count'),
            func.avg(func.nullif(Film.runtime, 0)).label('avg_runtime')
        )
        .join(base_films, Release.film_id == base_films.c.id)
        .join(Film, Film.id == base_films.c.id)
        .group_by('year')
        .order_by('year')
        .all()
    )
    releases_by_year_list = [
        {"year": int(y), "count": c, "avg_runtime": round(ar, 2) if ar else None}
        for y, c, ar in releases_by_year
    ]

    releases_by_month = (
        db.session.query(
            extract('month', Release.date).label('month'),
            func.count(Release.film_id).label('count'),
            func.avg(func.nullif(Film.runtime, 0)).label('avg_runtime')
        )
        .join(base_films, Release.film_id == base_films.c.id)
        .join(Film, Film.id == base_films.c.id)
        .group_by('month')
        .order_by('month')
        .all()
    )
    releases_by_month_list = [
        {"month": int(m), "count": c, "avg_runtime": round(ar, 2) if ar else None}
        for m, c, ar in releases_by_month
    ]

    films_by_year = (
        db.session.query(
            Film.release_year.label('year'),
            func.count(Film.id).label('count'),
            func.avg(func.nullif(Film.runtime, 0)).label('avg_runtime')
        )
        .join(base_films, Film.id == base_films.c.id)
        .filter(Film.release_year.isnot(None))
        .group_by(Film.release_year)
        .order_by(Film.release_year)
        .all()
    )
    films_by_year_list = [
        {"year": int(y), "count": c, "avg_runtime": round(ar, 2) if ar else None}
        for y, c, ar in films_by_year
    ]

    return {
        "releases_by_year": releases_by_year_list,
        "releases_by_month": releases_by_month_list,
        "films_by_year": films_by_year_list,
    }


def get_statistics(args=None):
    """Orchestrate collection of all film statistics.

    Builds a filtered film query, then delegates to specialized
    functions for different statistical categories.

    Args:
        args (dict, optional): Filter parameters from request.args.

    Returns:
        dict: Complete statistics with total, top, and grouped sections.
    """
    base_films = db.session.query(Film.id)

    if args:
        base_films = apply_film_filters(base_films, args)

    base_films = base_films.subquery()

    total_films = db.session.query(func.count()).select_from(base_films).scalar()

    basic_stats = get_basic_stats(base_films, total_films)
    releases = get_releases(base_films)
    person_stats = get_persons_stats(base_films)
    top_actors_by_gender, top_crew_by_gender = get_top_persons_by_role(base_films, limit=TOP_PERSONS_LIMIT)
    top_popular_films = get_popular_films(base_films)
    films_by_attributes = get_films_by_attributes(base_films)
    films_by_runtime_list = get_runtime_stats(base_films)

    grouped_releases = get_grouped_releases(base_films)

    return {
        "total": {
            "films": total_films,
            **basic_stats,
            **releases,
            **person_stats,
        },
        "top_actors_by_gender": top_actors_by_gender,
        "top_crew_by_gender": top_crew_by_gender,
        "top": {
             "popular": top_popular_films,
        },
        "grouped": {
            **grouped_releases,
            **films_by_attributes,
            "films_by_runtime": films_by_runtime_list,
        }
    }


@stats.route('/stats', methods=['GET'])
def get_stats():
    """Return comprehensive film statistics with optional filters.

    Aggregates data about films, releases, cast, and crew including
    totals, top lists, and grouped statistics. All results can be
    filtered using query parameters.

    Query Parameters:
        language (str): Filter by original language code.
        release_year (int): Filter by film release year.
        pt_release_year (int): Filter by Portuguese release year.
        month (int, 1-12): Filter by release month.
        runtime (str): Runtime filter. Format: "90-120", ">120", "<60", or exact number.
        genre (int): Filter by genre ID.
        country (str): Filter by country code (e.g., "PT", "US").
        distributor (str): Filter by distributor name.
        content_rating (str): Filter by rating. Format: "R-13" (hyphen converts to slash).
        cinema (str): Filter by cinema ID.

    Returns:
        dict: Statistics object containing:
            - total: Aggregate counts and percentages
            - top_actors_by_gender: Top actors per gender
            - top_crew_by_gender: Top crew per role and gender
            - top.popular: Most popular films
            - grouped: Data grouped by various dimensions

    Raises:
        BadRequest: If any query parameter is invalid.
    """
    return get_statistics(args=request.args)
