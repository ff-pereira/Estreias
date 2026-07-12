import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))
ALCHEMICAL_DATABASE_URL = os.environ.get('DATABASE_URL')

engine = create_engine(ALCHEMICAL_DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
