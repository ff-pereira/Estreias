"""
Welcome to the documentation for the Estreias API!

This project is written in Python, with the
[Flask](https://flask.palletsprojects.com/) web framework. This documentation
is generated automatically from the
[project's source code](https://github.com/ffpereira-fct/radio) using
the [APIFairy](https://github.com/miguelgrinberg/apifairy) Flask extension.

## Introduction

RadioStats is a **full-stack personal project** designed to analyze and visualize the most frequently played songs on Portuguese radio stations owned by the Bauer Media Group. 
Data is collected automatically and updated daily at **1 AM**, reflecting the previous day’s broadcasts.

RadioStats-API is an easy to use web API that serves as the backend for the [RadioStats](https://radiostats.ffpereira.com) project. 

It provides all the base features required to implement the frontend:

- List plays, songs, artists and radio stations
- Obtain most played, statistics and rankings for songs, artists and radio stations
- Fix data inconsistencies and merge no_mcr entries (no data provided by the radio stations)

## Configuration

The environment variables that are currently used are listed in the table below:

| Environment Variable | Default | Description |
| - | - | - |
| `SECRET_KEY` | `secretkey` | A secret key used when signing tokens. |
| `DATABASE_URL`  | `postgresql://user:password@host:port/dbname` | The database URL, as defined by the [SQLAlchemy](https://docs.sqlalchemy.org/en/14/core/engines.html#database-urls) framework. |
| `GEMINI_API_KEY` | not defined | Gemini API key to obtain data such as description and nationality from artists (optional) |

## Pagination

API endpoints that return collections of resources, such as the plays, songs or artists,
implement pagination, and the client must use query string arguments to specify
the range of items to return.

The number of items to return is specified by the `limit` argument, which is
optional. If not specified, the server sets the limit to a reasonable value for
the endpoint. If the limit is too large, the server may decide to use a lower
value instead. The following example shows how to request the first 10 users:

    http://localhost:5000/api/plays?limit=10

The `offset` argument is used to specify the zero-based index of the first item
to return. If not given, the server sets the offset to 0. The following example
shows how to request the second page of users with a page size of 10:

    http://localhost:5000/api/plays?limit=10&offset=10

Sometimes paginating with the `offset` argument can be inconvenient, such as
with collections where new elements are not always inserted at the end of the
list. As an alternative to `offset`, the `after` argument can be used to set
the start item to the item after the one specified. This API supports `after`
for most played and stats, which are sorted by their total played count.
The `after` argument must be set to a date specification in ISO 8601 format, 
such as `2025-11-19`. Examples:

    http://localhost:5000/api/songs/most_played?after=2025-08-05&before=2025-11-19
    http://localhost:5000/api/artists/most_played?after=2025-08-05&before=2025-11-19
    http://localhost:5000/api/stats?&after=2025-08-05&before=2025-11-19

The response body in a paginated request contains a `data` attribute that is
set to the list of entities that are in the requested page. A `pagination`
attribute is also included with `offset`, `limit`, `count` and `total`
sub-attributes, which enable the client to present pagination controls
to the user.

## Errors

All errors returned by this API use the following JSON structure:

```json
{
    "code": <numeric error code>,
    "message": <short error message>,
    "description": <longer error description>,
}
```

In the case of schema validation errors, an `errors` property is also returned,
containing a detailed list of validation errors found in the submitted request:

```json
{
    "code": <error code>,
    "message": <error message>,
    "description": <error description>,
    "errors": [ <error details>, ... ]
}
```

## Acknowledgements

This project's structure was inspired by Miguel Grinberg's excellent tutorial: [React Mega-Tutorial](https://blog.miguelgrinberg.com/post/introducing-the-react-mega-tutorial)

"""  # noqa: E501

from api.app import create_app, db, ma  # noqa: F401
