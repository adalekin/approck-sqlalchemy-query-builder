from typing import Iterator

import pytest
from sqlalchemy.orm import Session

from tests.models import Author, Base, Book, LocalSession, engine


@pytest.fixture(name="fx_session", autouse=True)
def fx_session_impl() -> Iterator[Session]:
    Base.metadata.create_all(engine)
    session = LocalSession()

    yield session

    session.rollback()
    session.close()


@pytest.fixture(name="fx_author")
def fx_author_impl(fx_session: Session) -> Author:
    author = Author(first_name="Paulo", last_name="Coelho", email="paulo_coelho@gmail.com")

    fx_session.add(author)
    fx_session.commit()

    return author


@pytest.fixture(name="fx_book")
def fx_book_impl(fx_session: Session, fx_author: Author) -> Book:
    book = Book(slug="alchemist", title="The Alchemist", author=fx_author)

    fx_session.add(book)
    fx_session.commit()

    return book
