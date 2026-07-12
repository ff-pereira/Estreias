"""
    author: ffpereira
    date: 2025-11-21
"""

from config import Config
from flask_cors import CORS
from apifairy import APIFairy
from alchemical.flask import Alchemical
from flask_marshmallow import Marshmallow
from flask import Flask, redirect, url_for

cors = CORS()
db = Alchemical()
ma = Marshmallow()
apifairy = APIFairy()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Extensions
    db.init_app(app)
    ma.init_app(app)
    cors.init_app(app)
    apifairy.init_app(app)

    # Blueprints
    from api.errors import errors
    app.register_blueprint(errors)

    from api.films import films
    app.register_blueprint(films, url_prefix='/api')

    from api.persons import persons
    app.register_blueprint(persons, url_prefix='/api')

    from api.genres import genres
    app.register_blueprint(genres, url_prefix='/api')

    from api.cinemas import cinemas
    app.register_blueprint(cinemas, url_prefix='/api')

    from api.countries import countries
    app.register_blueprint(countries, url_prefix='/api')

    from api.languages import languages
    app.register_blueprint(languages, url_prefix='/api')

    from api.content_ratings import content_ratings
    app.register_blueprint(content_ratings, url_prefix='/api')

    from api.distributors import distributors
    app.register_blueprint(distributors, url_prefix='/api')

    from api.stats import stats
    app.register_blueprint(stats, url_prefix='/api')

    from api.releases import releases
    app.register_blueprint(releases, url_prefix='/api')


    @app.route('/')
    def index():
        return redirect(url_for('apifairy.docs'))

    return app
