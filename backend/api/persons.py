"""
    author: ffpereira
    date: 2025-11-21
"""

from sqlalchemy import select, func, desc
from apifairy import response
from flask import Blueprint, abort, request
from apifairy.decorators import other_responses

from api import db
from api.decorators import paginated_response
from api.models import Film, Crew, Cast, Person
from api.schemas import PersonCountSchema, PersonSchema, StringPaginationSchema, PersonRolesSchema

persons = Blueprint('persons', __name__)

person_schema = PersonSchema()
persons_schema = PersonSchema(many=True)
person_roles_schema = PersonRolesSchema()

VALID_GENDERS = (1, 2, 3)
VALID_CREW_ROLES = {'director', 'writer', 'composer', 'cinematographer'}


@persons.route('/persons', methods=['GET'])
@paginated_response(persons_schema, order_by=Person.name,
                    order_direction='desc',
                    pagination_schema=StringPaginationSchema)
def list_persons():
    """List all persons with pagination.

    Returns a paginated list of all persons in the database, ordered by
    name in descending order.

    Returns:
        PaginatedResponse: A paginated list of Person objects.
    """
    return db.session.query(Person)


@persons.route('/person/<person_id>', methods=['GET'])
@response(person_schema)
@other_responses({404: 'Person not found', 400: 'Invalid parameters'})
def get_person(person_id):
    """Retrieve a person by their ID.

    Args:
        person_id (str): The ID of the person to retrieve. Will be
            converted to integer.

    Returns:
        Person: The person object if found.

    Raises:
        400: If the person ID is not a valid integer.
        404: If the person does not exist.
    """
    try:
        person_id = int(person_id)
    except ValueError:
        abort(400)

    return db.session.get(Person, person_id) or abort(404)


@persons.route('/person/roles/<person_id>', methods=['GET'])
@response(person_roles_schema)
@other_responses({404: 'Person not found', 400: 'Invalid parameters'})
def get_person_roles(person_id):
    """Retrieve role counts for a person by their ID.

    Returns counts of films where the person worked in various roles,
    including acting, directing, writing, sound, and camera work.

    Args:
        person_id (str): The ID of the person to retrieve roles for.

    Returns:
        dict: A dictionary with role categories as keys and film counts
            as values. Format: {
                'Actor': int,
                'Director': int,
                'Writer': int,
                'Sound': int,
                'Camera': int
            }

    Raises:
        400: If the person ID is not a valid integer.
        404: If the person ID does not exist.
    """
    try:
        person_id = int(person_id)
    except ValueError:
        abort(400)

    person = db.session.get(Person, person_id) or abort(404)

    return {
        'Actor': len(person.cast_roles),
        'Director': sum(1 for c in person.crew_roles if c.role == 'director'),
        'Writer': sum(1 for c in person.crew_roles if c.role == 'writer'),
        'Sound': sum(1 for c in person.crew_roles if c.role == 'composer'),
        'Camera': sum(1 for c in person.crew_roles if c.role == 'cinematographer'),
    }


@persons.route('/cast', methods=['GET'])
@paginated_response(
    PersonCountSchema,
    order_by=func.count(Cast.film_id),
    order_direction='desc'
)
@other_responses({400: 'Invalid gender'})
def cast_counts():
    """Retrieve cast counts with optional filtering.

    Returns a paginated list of cast members with their film counts,
    ordered by the number of films they've appeared in.

    Query Parameters:
        name (str, optional): Filter by person name (case-insensitive,
            partial match).
        gender (int, optional): Filter by gender. Valid values: 1, 2, 3.

    Returns:
        PaginatedResponse: A paginated list of objects containing
            id, name, and count of films.

    Raises:
        400: If an invalid gender is provided.
    """
    name_search = request.args.get('name')
    gender_filter = request.args.get('gender')

    gender_input = request.args.get('gender')

    if gender_input is not None:
        try:
            gender_filter = int(gender_input)
        except ValueError:
            abort(400, description="Gender must be an integer")

        if gender_filter not in VALID_GENDERS:
            abort(400, description="Invalid gender. Must be one of: 1, 2, 3")
    else:
        gender_filter = None

    stmt = (
        select(
            Person.id.label("id"),
            Person.name.label("name"),
            func.count(Cast.film_id).label("count"),
        )
        .join(Cast)
        .group_by(Person.id, Person.name)
        .order_by(
            desc(func.count(Cast.film_id)),
            Person.id.asc(),
        )
    )

    if gender_filter:
        stmt = stmt.where(Person.gender == gender_filter)

    if name_search:
        name_search = name_search.strip()
        if name_search:
            stmt = stmt.where(Person.name.ilike(f'%{name_search}%'))

    return stmt


@persons.route('/crew', methods=['GET'])
@paginated_response(
    PersonCountSchema,
    order_by=func.count(Crew.film_id),
    order_direction='desc'
)
@other_responses({400: 'Invalid gender or role'})
def crew_counts():
    """Retrieve crew counts with optional filtering.

    Returns a paginated list of crew members with their film counts,
    ordered by the number of films they've worked on.

    Query Parameters:
        name (str, optional): Filter by person name (case-insensitive,
            partial match).
        role (str, optional): Filter by crew role. Must be one of:
            director, writer, composer, cinematographer, editor, producer.
        gender (int, optional): Filter by gender. Valid values: 1, 2, 3.

    Returns:
        PaginatedResponse: A paginated list of objects containing
            id, name, and count of films.

    Raises:
        400: If an invalid gender or role is provided.
    """
    name_search = request.args.get('name')
    role_search = request.args.get('role')
    gender_input = request.args.get('gender')

    if gender_input is not None:
        try:
            gender_filter = int(gender_input)
        except ValueError:
            abort(400, description="Gender must be an integer")

        if gender_filter not in VALID_GENDERS:
            abort(400, description="Invalid gender. Must be one of: 1, 2, 3")
    else:
        gender_filter = None

    if role_search:
        role_search = role_search.lower().strip()
        if role_search not in VALID_CREW_ROLES:
            abort(400, description=f"Invalid role. Must be one of: {', '.join(sorted(VALID_CREW_ROLES))}")

    stmt = (
        select(
            Person.id.label("id"),
            Person.name.label("name"),
            func.count(Crew.film_id).label("count"),
        )
        .join(Crew)
        .group_by(Person.id, Person.name)
        .order_by(
            desc(func.count(Crew.film_id)),
            Person.id.asc(),
        )
    )

    if gender_filter:
        stmt = stmt.where(Person.gender == gender_filter)

    if role_search:
        stmt = stmt.where(Crew.role == role_search)

    if name_search:
        name_search = name_search.strip()
        if name_search:
            stmt = stmt.where(Person.name.ilike(f'%{name_search}%'))

    return stmt
