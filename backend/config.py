import os
from dotenv import load_dotenv

load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Database options
    ALCHEMICAL_DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://user:password@host:port/dbname')

    # Security options
    SECRET_KEY = os.environ.get('SECRET_KEY', 'secretkey')

    TMDB_API_KEY = os.environ.get('TMDB_API_KEY')

    # API documentation
    APIFAIRY_TITLE = 'Estreias API'
    APIFAIRY_VERSION = '1.0.0'
    APIFAIRY_UI = os.environ.get('DOCS_UI', 'elements')