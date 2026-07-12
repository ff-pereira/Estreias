"""
    author: ffpereira
    date: 2025-11-21
"""

import sqlalchemy as sa
from flask import url_for
from alchemical import Model
from sqlalchemy.sql import func
from sqlalchemy import orm as so
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from sqlalchemy import Table, Column, ForeignKey


film_countries = Table(
    'film_countries', Model.metadata,
    Column('film_id', sa.Text, ForeignKey('films.id'), primary_key=True),
    Column('country_id', sa.Text, ForeignKey('countries.id'), primary_key=True),
)

film_spoken_languages = Table(
    'film_spoken_languages', Model.metadata,
    Column('film_id', sa.Text, ForeignKey('films.id'), primary_key=True),
    Column('language_id', sa.Text, ForeignKey('languages.id'), primary_key=True),
)

film_genres = Table(
    'film_genres', Model.metadata,
    Column('film_id', sa.Text, ForeignKey('films.id'), primary_key=True),
    Column('genre_id', sa.Integer, ForeignKey('genres.id'), primary_key=True),
)


class Film(Model):
    __tablename__ = 'films'

    id: so.Mapped[str] = so.mapped_column(sa.Text, primary_key=True)
    imdb_id: so.Mapped[str] = so.mapped_column(sa.String(32), nullable=True)
    tmdb_id: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=True)
    title: so.Mapped[str] = so.mapped_column(sa.Text, nullable=False)
    original_title: so.Mapped[str] = so.mapped_column(sa.Text, nullable=False)
    portuguese_title: so.Mapped[str] = so.mapped_column(sa.Text, nullable=True)
    release_year: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=True, index=True)
    release_date: so.Mapped[date] = so.mapped_column(sa.Date, nullable=True, index=True)
    runtime: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=True)
    content_rating: so.Mapped[str] = so.mapped_column(sa.String(32), nullable=True)
    description: so.Mapped[str] = so.mapped_column(sa.Text, nullable=True)
    portuguese_description: so.Mapped[str] = so.mapped_column(sa.Text, nullable=True)
    distributor: so.Mapped[str] = so.mapped_column(sa.Text, nullable=True, index=True)
    original_language: so.Mapped[str] = so.mapped_column(sa.String(8), sa.ForeignKey("languages.id"), nullable=True, index=True)
    tagline: so.Mapped[str] = so.mapped_column(sa.Text, nullable=True)
    budget: so.Mapped[int] = so.mapped_column(sa.BigInteger, nullable=True)
    revenue: so.Mapped[int] = so.mapped_column(sa.BigInteger, nullable=True)
    in_cinemas: so.Mapped[bool] = so.mapped_column(sa.Boolean, nullable=False, default=False)
    updated_at: so.Mapped[datetime] = so.mapped_column(
        sa.DateTime(timezone=True),
        nullable=True,
        index=True,
        server_default=func.now(),
        onupdate=func.now()
    )

    screenings: so.Mapped[list["Screening"]] = so.relationship('Screening', back_populates='film', lazy="selectin")
    genres: so.Mapped[list["Genre"]] = so.relationship('Genre', secondary=film_genres, back_populates='films', lazy="selectin")
    cast: so.Mapped[list["Cast"]] = so.relationship('Cast', back_populates='film', order_by="Cast.order", cascade='all, delete-orphan', lazy="selectin")
    crew: so.Mapped[list["Crew"]] = so.relationship('Crew', back_populates='film', cascade='all, delete-orphan', lazy="selectin")
    countries: so.Mapped[list["Country"]] = so.relationship('Country', secondary=film_countries, back_populates='films', lazy="selectin")
    releases: so.Mapped[list["Release"]] = so.relationship('Release', back_populates='film', cascade='all, delete-orphan', lazy="selectin")
    spoken_languages: so.Mapped[list["Language"]] = so.relationship('Language', secondary=film_spoken_languages, back_populates='films', lazy="selectin")
    cinemas: so.Mapped[list["Cinema"]] = so.relationship('Cinema', secondary='screenings', back_populates='films', viewonly=True, lazy="selectin")
    original_language_obj: so.Mapped["Language"] = so.relationship("Language", lazy="joined")

    @property
    def url(self):
        return url_for('films.get_film', film_id=self.id)

    @property
    def poster(self):
        return url_for('static', filename=f"images/posters/original/{self.id}.jpg", _external=True)

    @property
    def backdrop(self):
        return url_for('static', filename=f"images/posters/backdrop/{self.id}.jpg", _external=True)

    @property
    def upcoming(self):
        """True if the film's release date in Portugal (country_id='PT') is in the future."""
        pt_release = next((r for r in self.releases if r.country_id == 'PT'), None)
        if not pt_release:
            return False  # No PT release, assume not future
        return pt_release.date > date.today()

    @property
    def pt_release_date(self):
        pt_release = next((r for r in self.releases if r.country_id == 'PT'), None)
        return pt_release.date if pt_release else None


class Cast(Model):
    __tablename__ = 'cast'

    person_id: so.Mapped[int] = so.mapped_column(sa.Integer, sa.ForeignKey('persons.id'), primary_key=True, index=True)
    film_id: so.Mapped[str] = so.mapped_column(sa.Text, sa.ForeignKey('films.id'), primary_key=True, index=True)
    character: so.Mapped[str] = so.mapped_column(sa.Text, nullable=True)
    order: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=True)

    film: so.Mapped["Film"] = so.relationship('Film', back_populates='cast', lazy="selectin")
    person: so.Mapped["Person"] = so.relationship('Person', back_populates='cast_roles', lazy="selectin")


class Crew(Model):
    __tablename__ = 'crew'

    person_id: so.Mapped[int] = so.mapped_column(sa.Integer, sa.ForeignKey('persons.id'), primary_key=True)
    film_id: so.Mapped[str] = so.mapped_column(sa.Text, sa.ForeignKey('films.id'), primary_key=True, index=True)
    role: so.Mapped[str] = so.mapped_column(sa.Text, primary_key=True, index=True)

    film: so.Mapped["Film"] = so.relationship('Film', back_populates='crew', lazy="selectin")
    person: so.Mapped["Person"] = so.relationship('Person', back_populates='crew_roles', lazy="selectin")


class Person(Model):
    __tablename__ = 'persons'

    id: so.Mapped[int] = so.mapped_column(sa.Integer, primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.Text, index=True)
    original_name: so.Mapped[str] = so.mapped_column(sa.Text, nullable=True)
    gender: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=True, index=True)

    imdb_id: so.Mapped[str] = so.mapped_column(sa.String(32), nullable=True)
    pob: so.Mapped[str] = so.mapped_column(sa.Text, nullable=True)
    known_for_department: so.Mapped[str] = so.mapped_column(sa.Text, nullable=True)
    popularity: so.Mapped[float] = so.mapped_column(sa.Float, nullable=True, default=0.0)
    birthday: so.Mapped[date] = so.mapped_column(sa.Date, default=None, nullable=True)
    deathday: so.Mapped[date] = so.mapped_column(sa.Date, default=None, nullable=True)
    biography: so.Mapped[str] = so.mapped_column(sa.Text, nullable=True)
    updated_at: so.Mapped[datetime] = so.mapped_column(sa.DateTime, default=None, nullable=True)

    cast_roles: so.Mapped[list["Cast"]] = so.relationship('Cast', back_populates='person', cascade='all, delete-orphan', lazy="selectin")
    crew_roles: so.Mapped[list["Crew"]] = so.relationship('Crew', back_populates='person', cascade='all, delete-orphan', lazy="selectin")

    # Optional relationships
    acted_in: so.Mapped[list["Film"]] = so.relationship(
        'Film',
        secondary='cast',
        primaryjoin=id == Cast.person_id,
        secondaryjoin=Cast.film_id == Film.id,
        viewonly=True,
        lazy="selectin")
    worked_on: so.Mapped[list["Film"]] = so.relationship(
        'Film',
        secondary='crew',
        primaryjoin=id == Crew.person_id,
        secondaryjoin=Crew.film_id == Film.id,
        viewonly=True,
        lazy="selectin"
    )

    @property
    def age_delta(self):
        if not self.birthday:
            return None
        end = self.deathday or date.today()
        return relativedelta(end, self.birthday)


class Country(Model):
    __tablename__ = 'countries'

    id: so.Mapped[str] = so.mapped_column(sa.Text, primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.Text, nullable=True)

    films: so.Mapped[list["Film"]] = so.relationship('Film', secondary=film_countries, back_populates='countries', lazy="selectin")

    @property
    def flag(self):
        return url_for('static', filename=f'flags/{self.id.lower()}.png', _external=True)


class Language(Model):
    __tablename__ = 'languages'

    id: so.Mapped[str] = so.mapped_column(sa.Text, primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.Text, nullable=True)
    english_name: so.Mapped[str] = so.mapped_column(sa.Text, nullable=True)

    films: so.Mapped[list["Film"]] = so.relationship('Film', secondary=film_spoken_languages, back_populates='spoken_languages', lazy="selectin")


class Genre(Model):
    __tablename__ = 'genres'

    id: so.Mapped[int] = so.mapped_column(sa.Integer, primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.Text, nullable=True)

    films: so.Mapped[list["Film"]] = so.relationship('Film', secondary=film_genres, back_populates='genres', lazy="selectin")


class Cinema(Model):
    __tablename__ = 'cinemas'

    id: so.Mapped[str] = so.mapped_column(sa.Text, primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.Text, nullable=False)
    group: so.Mapped[str] = so.mapped_column(sa.Text, nullable=True, index=True)

    latitude: so.Mapped[float] = so.mapped_column(sa.Float, nullable=True)
    longitude: so.Mapped[float] = so.mapped_column(sa.Float, nullable=True)
    street_address: so.Mapped[str] = so.mapped_column(sa.Text, nullable=True)
    postal_code: so.Mapped[str] = so.mapped_column(sa.Text, nullable=True)
    address_region: so.Mapped[str] = so.mapped_column(sa.Text, nullable=True)
    address_country: so.Mapped[str] = so.mapped_column(sa.Text, nullable=True)
    address_locality: so.Mapped[str] = so.mapped_column(sa.Text, nullable=True)
    telephone: so.Mapped[str] = so.mapped_column(sa.Text, nullable=True)

    country_id: so.Mapped[str] = so.mapped_column(sa.Text, sa.ForeignKey('countries.id'), nullable=True, index=True)

    screenings: so.Mapped[list["Screening"]] = so.relationship('Screening', back_populates='cinema', lazy="selectin")
    films: so.Mapped[list["Film"]] = so.relationship('Film', secondary='screenings', back_populates='cinemas', viewonly=True, lazy="selectin")


class Screening(Model):
    __tablename__ = 'screenings'

    film_id: so.Mapped[str] = so.mapped_column(sa.Text, ForeignKey('films.id'), primary_key=True)
    cinema_id: so.Mapped[str] = so.mapped_column(sa.Text, ForeignKey('cinemas.id'), primary_key=True, index=True)
    first_seen: so.Mapped[date] = so.mapped_column(sa.Date, nullable=False)
    last_seen: so.Mapped[date] = so.mapped_column(sa.Date, nullable=True)

    film: so.Mapped["Film"] = so.relationship('Film', back_populates='screenings', lazy="selectin")
    cinema: so.Mapped["Cinema"] = so.relationship('Cinema', back_populates='screenings', lazy="selectin")


class Release(Model):
    __tablename__ = 'releases'

    film_id: so.Mapped[str] = so.mapped_column(sa.Text, sa.ForeignKey('films.id'), primary_key=True, index=True)
    country_id: so.Mapped[str] = so.mapped_column(sa.Text, sa.ForeignKey('countries.id'), primary_key=True, index=True)
    date: so.Mapped[date] = so.mapped_column(sa.Date, nullable=False, index=True)
    title: so.Mapped[str] = so.mapped_column(sa.Text, nullable=True)
    popularity: so.Mapped[float] = so.mapped_column(sa.Float, nullable=False, default=0.0)

    film: so.Mapped["Film"] = so.relationship('Film', back_populates='releases', lazy="selectin")

    @property
    def poster(self):
        return url_for('static', filename=f"images/posters/original/{self.film_id}.jpg", _external=True)


sa.Index("ix_film_countries_country_id", film_countries.c.country_id)
sa.Index("ix_film_genres_genre_id", film_genres.c.genre_id)
sa.Index("ix_crew_film_role", Crew.film_id, Crew.role)
