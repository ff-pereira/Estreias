from flask import abort
import sqlalchemy as sqla
from functools import wraps
from apifairy import arguments, response

from api.app import db
from api.schemas import StringPaginationSchema, PaginatedCollection


def paginated_response(schema, default_limit=60, max_limit=200, order_by=None,
                       order_direction='asc',
                       pagination_schema=StringPaginationSchema):
    def inner(f):
        @wraps(f)
        def paginate(*args, **kwargs):
            args = list(args)
            pagination = args.pop(-1)
            select_query = f(*args, **kwargs)

            if order_by is not None:
                o = order_by.desc() if order_direction == 'desc' else order_by
                select_query = select_query.order_by(o)

            count = db.session.scalar(sqla.select(sqla.func.count()).select_from(select_query.subquery()))

            limit = pagination.get('limit', default_limit)
            offset = pagination.get('offset')

            if limit > max_limit:
                limit = max_limit

            if offset is None:
                offset = 0
            if offset < 0 or (count > 0 and offset >= count) or limit <= 0:
                abort(400)

            query = select_query.limit(limit).offset(offset)

            if hasattr(query, "statement"):
                query = query.statement
            result = db.session.execute(query)

            if len(result.keys()) == 1:
                data = result.scalars().all()
            else:
                data = result.mappings().all()

            return {'data': data, 'pagination': {
                'offset': offset,
                'limit': limit,
                'count': len(data),
                'total': count,
            }}

        return arguments(pagination_schema)(response(PaginatedCollection(
            schema, pagination_schema=pagination_schema))(paginate))

    return inner
