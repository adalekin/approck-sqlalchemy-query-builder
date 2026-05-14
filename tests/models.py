import datetime
import re

import sqlalchemy as sa
from sqlalchemy import MetaData
from sqlalchemy.orm import as_declarative, declared_attr, relationship, sessionmaker
from sqlalchemy.pool import StaticPool

SNAKE_CASE_RE = re.compile(r"(?<!^)(?=[A-Z])")


@as_declarative()
class Base(object):
    __name__: str
    metadata: MetaData

    @classmethod
    @declared_attr
    def __tablename__(cls):  # noqa: N805
        return SNAKE_CASE_RE.sub("_", cls.__name__).lower()


class Author(Base):
    id = sa.Column(sa.Integer(), primary_key=True)
    first_name = sa.Column(sa.String(100))
    last_name = sa.Column(sa.String(100))
    email = sa.Column(sa.String(255), nullable=False)
    joined = sa.Column(sa.DateTime(), default=datetime.datetime.utcnow)


class Book(Base):
    id = sa.Column(sa.Integer(), primary_key=True)
    slug = sa.Column(sa.String(100), nullable=False)
    title = sa.Column(sa.String(100), nullable=False)

    author_id = sa.Column(sa.Integer(), sa.ForeignKey("author.id"))
    author = relationship("Author", lazy="selectin")

    created_at = sa.Column(sa.DateTime(), default=datetime.datetime.utcnow)
    updated_at = sa.Column(sa.DateTime(), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    description = sa.Column(sa.Text)


engine = sa.create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
LocalSession = sessionmaker(bind=engine)
