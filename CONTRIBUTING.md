# Contributing

Thanks for your interest in improving this project.

## Workflow

1. Open an issue to describe the bug or feature, or comment on an existing one.
2. Fork the repository and create a branch from `main`.
3. Install the dev environment: `uv sync --group dev`.
4. Make changes and keep them focused on one concern per pull request.
5. Run checks locally:

   ```bash
   uv run pytest
   uv run ruff check .
   uv run ruff format .
   uv run mypy approck_sqlalchemy_query_builder
   ```

6. Open a pull request against `main` with a clear description of the change and why it is needed.

## Code style

- Formatting and linting use [Ruff](https://docs.astral.sh/ruff/) (see `ruff.toml`).
- Type hints are checked with [mypy](https://mypy-lang.org/) using the SQLAlchemy and Pydantic plugins where applicable.
