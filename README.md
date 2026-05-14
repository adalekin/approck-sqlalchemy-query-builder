# approck-sqlalchemy-query-builder

Take a **filter tree as JSON** (from a REST body, WebSocket message, or stored config), validate it with [Pydantic](https://docs.pydantic.dev/), and turn it into a SQLAlchemy 2 **`WHERE`** fragment you can attach to your own `select()`. You keep full control over columns, joins, and ordering; the library only maps allowed fields to real `Column` objects so arbitrary JSON never touches the database layer directly.

## Requirements

- Python 3.10+
- SQLAlchemy 2.0+
- Pydantic 2.x

## Install

```bash
pip install approck-sqlalchemy-query-builder
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv add approck-sqlalchemy-query-builder
```

## Usage

**1. Define the filter in JSON** — nested groups use `condition` (`"AND"` / `"OR"`) and `rules`; each leaf is `id` (logical name), `operator`, and `value`:

```json
{
  "condition": "AND",
  "rules": [
    { "id": "status", "operator": "=", "value": "active" },
    {
      "condition": "OR",
      "rules": [
        { "id": "role", "operator": "=", "value": "admin" },
        { "id": "role", "operator": "=", "value": "moderator" }
      ]
    }
  ]
}
```

**2. Parse and bind to real columns** — `Query.model_validate_json` / `Query.model_validate` accept the same shape as `json.loads`. You pass a whitelist `map_columns` from logical `id` to SQLAlchemy columns (only those keys can appear in SQL):

```python
import sqlalchemy as sa
from approck_sqlalchemy_query_builder import Query, query_filter

# Dict from your stack: JSON.parse, await request.json(), Pydantic/FastAPI body, etc.
filter_payload = {
    "condition": "AND",
    "rules": [
        {"id": "status", "operator": "=", "value": "active"},
        {
            "condition": "OR",
            "rules": [
                {"id": "role", "operator": "=", "value": "admin"},
                {"id": "role", "operator": "=", "value": "moderator"},
            ],
        },
    ],
}
query = Query.model_validate(filter_payload)

statement = sa.select(MyModel)
statement = query_filter(
    statement,
    map_columns={
        "status": MyModel.status,
        "role": MyModel.role,
    },
    query=query,
)
```

For a raw JSON string (e.g. straight from the wire), use `Query.model_validate_json(body)`.

### Supported operators

`=`, `>`, `<`, `>=`, `<=`, `!=`, `in`, `not in`.

### Datetime columns

If the column type name contains `DATETIME`, integer values are treated as Unix timestamps (milliseconds if the value is larger than “now” in seconds). Strings are parsed with `python-dateutil` and normalized to UTC.

### Unknown columns

With `skip_unknown_column=True`, rules whose `id` is missing from `map_columns` are skipped instead of raising `ValueError`.

## Development

Clone the repository and install dependencies with uv:

```bash
uv sync --group dev
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy approck_sqlalchemy_query_builder
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for pull request guidelines.

## License

MIT — see [LICENSE](LICENSE).
