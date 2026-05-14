import pytest
import sqlalchemy as sa
from sqlalchemy.orm import Session

from approck_sqlalchemy_query_builder import Query, query_filter
from tests.models import Author, Book


@pytest.mark.parametrize(
    "filter_query,result_len",
    [
        (
            Query(
                **{
                    "condition": "AND",
                    "rules": [
                        {
                            "id": "author.last_name",
                            "operator": "=",
                            "value": "???",
                        }
                    ],
                }
            ),
            0,
        ),
        (
            Query(
                **{
                    "condition": "AND",
                    "rules": [
                        {
                            "id": "author.last_name",
                            "operator": "=",
                            "value": "Coelho",
                        }
                    ],
                }
            ),
            1,
        ),
        (
            Query(
                **{
                    "condition": "OR",
                    "rules": [
                        {
                            "id": "author.last_name",
                            "operator": "=",
                            "value": "Coelho",
                        },
                        {
                            "id": "author.last_name",
                            "operator": "=",
                            "value": "Borges",
                        },
                    ],
                }
            ),
            1,
        ),
        (
            Query(
                **{
                    "condition": "AND",
                    "rules": [],
                }
            ),
            1,
        ),
        (
            Query(
                **{
                    "condition": "AND",
                    "rules": [
                        {
                            "id": "book.created_at",
                            "operator": "<",
                            "value": 1707767532000,
                        }
                    ],
                }
            ),
            0,
        ),
        (
            Query(
                **{
                    "condition": "AND",
                    "rules": [
                        {
                            "id": "book1.created_at",
                            "operator": "<",
                            "value": 1707767532000,
                        }
                    ],
                }
            ),
            1,
        ),
    ],
)
def test_query_filter(
    filter_query: Query,
    fx_session: Session,
    result_len: int,
):
    # FIXME: avoid duplicates in the parametrized test
    author = Author(first_name="Paulo", last_name="Coelho", email="paulo_coelho@gmail.com")
    fx_session.add(author)

    book = Book(slug="alchemist", title="The Alchemist", author=author)
    fx_session.add(book)
    fx_session.commit()

    statement = query_filter(
        statement=sa.select(Book).join(Book.author),
        map_columns={
            "author.last_name": Author.last_name,
            "book.created_at": Book.created_at,
        },
        query=filter_query,
        skip_unknown_column=True,
    )

    books = (fx_session.scalars(statement=statement)).unique().all()
    assert len(books) == result_len

    fx_session.delete(book)
    fx_session.delete(author)
    fx_session.commit()
