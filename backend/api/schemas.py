"""
    author: ffpereira
    date: 2025-11-21
"""
from datetime import date

from api import ma, db
from api.models import Film, Release, Cast, Crew, Language, Genre, Screening, Person, Cinema, Country
from flask import url_for
from marshmallow import validates_schema, ValidationError, fields, missing

paginated_schema_cache = {}


class EmptySchema(ma.Schema):
    pass


class DatePaginationSchema(ma.Schema):
    class Meta:
        ordered = True

    limit = ma.Integer()
    offset = ma.Integer()
    after = ma.Date(load_only=True)
    before = ma.Date(load_only=True)
    count = ma.Integer(dump_only=True)
    total = ma.Integer(dump_only=True)


class StringPaginationSchema(ma.Schema):
    class Meta:
        ordered = True

    limit = ma.Integer()
    offset = ma.Integer()
    count = ma.Integer(dump_only=True)
    total = ma.Integer(dump_only=True)


def PaginatedCollection(schema, pagination_schema=StringPaginationSchema):
    if schema in paginated_schema_cache:
        return paginated_schema_cache[schema]

    class PaginatedSchema(ma.Schema):
        class Meta:
            ordered = True

        pagination = ma.Nested(pagination_schema)
        data = ma.Nested(schema, many=True)

    PaginatedSchema.__name__ = 'Paginated{}'.format(schema.__class__.__name__)
    paginated_schema_cache[schema] = PaginatedSchema
    return PaginatedSchema


class CinemaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Cinema
        ordered = True

    picture = fields.Method("get_picture")
    group_picture = fields.Method("get_group_picture")

    def get_picture(self, obj):
        return url_for('static', filename=f"images/cinemas/{obj.id}.jpg", _external=True)

    def get_group_picture(self, obj):
        if obj.group:
            return url_for('static', filename=f"images/cinemas/{obj.group}.jpg", _external=True)


class CinemaWithCountSchema(ma.SQLAlchemyAutoSchema):
    id = fields.Str()
    name = fields.Str()
    group = fields.Str()
    film_count = fields.Int()

    brand = fields.Method("get_brand")

    def get_brand(self, obj):
        if obj.group:
            return url_for('static', filename=f"images/cinemas/{obj.group}.jpg", _external=True)
        else:
            return missing


class ReleasesPaginationSchema(ma.Schema):
    class Meta:
        ordered = True

    offset = ma.Integer()
    cinemas = ma.String()
    after = ma.String()
    before = ma.String()
    limit = ma.Integer()
    title_search = ma.String()


class ReleaseSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Release
        ordered = True

    film_id = ma.String(required=True)
    country_id = ma.String()
    date = ma.Date(required=True)
    title = ma.String()
    popularity = ma.Float()


class PersonSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Person
        ordered = True

    portrait = ma.Method("get_portrait")
    cast_roles = ma.Method("get_cast_roles")
    crew_roles = ma.Method("get_crew_roles_grouped")
    age = ma.Method("get_age")

    def get_portrait(self, obj):
        return url_for('static',filename=f"images/persons/w500/{obj.id}.jpg", _external=True)

    def get_cast_roles(self, obj):
        schema = CastSchema()
        roles = sorted(obj.cast_roles,key=lambda c: c.film.pt_release_date or date.min,reverse=True)
        return schema.dump(roles, many=True)

    def get_crew_roles_grouped(self, obj):
        grouped: dict[str, list[dict]] = {}
        schema = CrewSchema()

        roles = sorted( obj.crew_roles,key=lambda c: c.film.pt_release_date or date.min, reverse=True)

        for crew in roles:
            grouped.setdefault(crew.role, []).append(schema.dump(crew))

        return grouped

    def get_age(self, obj):
        d = obj.age_delta
        if not d:
            return None
        return f"{d.years} Years, {d.months} Months, {d.days} Days"


class PersonCountSchema(ma.Schema):
    id = fields.Int()
    name = fields.Str()
    count = fields.Int()

    portrait = fields.Method("get_portrait")

    def get_portrait(self, obj):
        return url_for('static',filename=f"images/persons/w300/{obj.id}.jpg", _external=True)


class CastSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Cast
        ordered = True

    film_id = ma.String()
    pt_release_date = ma.Date(attribute="film.pt_release_date", dump_only=True)
    upcoming = ma.Boolean(attribute="film.upcoming", dump_only=True)
    in_cinemas = ma.Boolean(attribute="film.in_cinemas", dump_only=True)
    # title = ma.String(attribute="film.title", dump_only=True)
    poster = ma.String(attribute="film.poster", dump_only=True)


class CrewSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Crew
        ordered = True

    film_id = ma.String()
    pt_release_date = ma.Date(attribute="film.pt_release_date", dump_only=True)
    upcoming = ma.Boolean(attribute="film.upcoming", dump_only=True)
    in_cinemas = ma.Boolean(attribute="film.in_cinemas", dump_only=True)
    poster = ma.String(attribute="film.poster", dump_only=True)


class LanguageSchema(ma.Schema):
    id = fields.Str(required=True)
    name = fields.Str(required=True, attribute="english_name")


class GenreSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Genre
        include_relationships = False

    id = ma.auto_field()
    name = ma.auto_field()


class ContentRatingSchema(ma.Schema):
    id = fields.Str(required=True)
    name = fields.Str(required=True)


class CountrySchema(ma.SQLAlchemySchema):
    class Meta:
        model = Country
        include_relationships = False

    id = ma.auto_field()
    name = ma.auto_field()
    flag = fields.Str()


class CountSchema(ma.SQLAlchemyAutoSchema):
    id = fields.Str()
    name = fields.Str()
    film_count = fields.Int()


class DistributorSchema(ma.Schema):
    id = fields.Str(required=True)
    name = fields.Str(required=True)


class FilmScreeningSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Screening
        ordered = True

    cinema_id = ma.String()
    cinema_name = ma.String(attribute="cinema.name", dump_only=True)


class FilmCastSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Cast
        ordered = True

    person_id = ma.Integer()
    person_name = ma.String(attribute="person.name", dump_only=True)
    character = ma.String()
    order = ma.Integer()

    portrait = fields.Method("get_portrait")

    def get_portrait(self, obj):
        return url_for('static', filename=f"images/persons/w300/{obj.person_id}.jpg", _external=True)


class FilmCrewSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Crew
        ordered = True

    person_id = ma.Integer()
    person_name = ma.String(attribute="person.name", dump_only=True)
    role = ma.String()

    portrait = fields.Method("get_portrait")

    def get_portrait(self, obj):
        return url_for('static', filename=f"images/persons/w300/{obj.person_id}.jpg", _external=True)


class FilmSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Film
        ordered = True
        exclude = ("updated_at", "portuguese_description", "releases",)

    poster = ma.String()
    backdrop = ma.String()

    cast = ma.List(ma.Nested(FilmCastSchema), dump_only=True)
    crew = ma.List(ma.Nested(FilmCrewSchema), dump_only=True)

    pt_release_date = ma.Date(attribute="pt_release_date", dump_only=True)

    original_language_obj = ma.Nested(LanguageSchema, dump_only=True)

    upcoming = ma.Boolean(attribute="upcoming", dump_only=True)

    genres = ma.List(ma.Nested(GenreSchema), dump_only=True)
    countries = ma.List(ma.Nested(CountrySchema), dump_only=True)
    screenings = ma.List(ma.Nested(FilmScreeningSchema), dump_only=True)
    spoken_languages = ma.List(ma.Nested(LanguageSchema), dump_only=True)


class SimplifiedFilmSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Film
        ordered = True
        exclude = ("updated_at", "description", "portuguese_description", "cast", "crew", "screenings", "spoken_languages",
                   "portuguese_title", "imdb_id", "tmdb_id", "tagline", "original_title", "releases", "genres", "countries", )

    poster = ma.String()
    pt_release_date = ma.Date(attribute="pt_release_date", dump_only=True)
    upcoming = ma.Boolean(attribute="upcoming", dump_only=True)
    # genres = ma.List(ma.Nested(GenreSchema), dump_only=True)
    # countries = ma.List(ma.Nested(CountrySchema), dump_only=True)


class CinemaNowShowingFilmSchema(ma.Schema):
    id = fields.String(required=True)
    title = fields.String(required=True)
    poster = fields.String()
    url = fields.String()
    runtime = fields.Integer()
    release_year = fields.Integer()
    first_seen = fields.Date(allow_none=True)
    last_seen = fields.Date(allow_none=True)


class CitySchema(ma.Schema):
    id = fields.Str()
    name = fields.Str()

class CitiesResponseSchema(ma.Schema):
    data = fields.List(fields.Nested(CitySchema))

class RegionWithCountSchema(ma.Schema):
    id = fields.Str(allow_none=True)
    name = fields.Str(allow_none=True)
    count = fields.Int()

class RegionsResponseSchema(ma.Schema):
    data = fields.List(fields.Nested(RegionWithCountSchema))


class GroupSchema(ma.Schema):
    id = fields.Str()
    name = fields.Str()

class GroupsResponseSchema(ma.Schema):
    data = fields.List(fields.Nested(GroupSchema))


class PersonRolesSchema(ma.Schema):
    Actor = fields.Int(required=True)
    Director = fields.Int(required=True)
    Writer = fields.Int(required=True)
    Sound = fields.Int(required=True)
    Camera = fields.Int(required=True)


class MetadataFilterSchema(ma.Schema):
    in_cinemas = fields.Str(required=False)
    title = fields.Str(required=False)
    genres = fields.Str(required=False)
    countries = fields.Str(required=False)
    distributors = fields.Str(required=False)
    content_ratings = fields.Str(required=False)
    language = fields.Str(required=False)