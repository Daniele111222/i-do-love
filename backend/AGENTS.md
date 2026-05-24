# AI News Hub - Backend Agent Guide

## Architecture Status

The backend is a FastAPI service using SQLAlchemy 2.0 async ORM, Pydantic v2 schemas,
JWT authentication, PostgreSQL, Redis, and planned Qdrant/RAG support.

Current architectural direction: keep API routes thin, place business logic in services,
use typed dependency contexts, and make health/security checks reflect real runtime state.

## Directory Map

| Area | Path | Responsibility |
| --- | --- | --- |
| API routes | `app/api/v1/` | HTTP request/response handling only |
| Services | `app/services/` | Business logic, transactions, expected domain errors |
| Models | `app/models/` | SQLAlchemy models and shared declarative `Base` |
| Schemas | `app/schemas/` | Pydantic request, response, and dependency context types |
| Core | `app/core/` | Configuration and security primitives |
| Dependencies | `app/dependencies.py` | FastAPI dependency wiring |
| Tests | `tests/` | Async API and service behavior tests |

## Hard Architecture Rules

1. API route modules must stay thin.
   - Allowed: request parsing, dependency injection, response schema selection, HTTP exception mapping.
   - Not allowed: direct business workflows, password hashing, token creation, persistence orchestration.

2. Business logic must live in `app/services/`.
   - Route handlers call service methods.
   - Services may use SQLAlchemy sessions and model queries.
   - Services raise typed exceptions from `app/services/exceptions.py`; routes convert them to HTTP status codes.

3. Do not pass untyped auth dictionaries.
   - Use `app.schemas.user.CurrentUser` for authenticated user context.
   - `get_current_user` must validate the access token and confirm the user is active in the database.

4. SQLAlchemy model base belongs in `app/models/base.py`.
   - New models must inherit from `app.models.base.Base`.
   - Export new models from `app/models/__init__.py` so metadata discovery remains predictable.

5. Health checks must be real.
   - `/health` may check process liveness only.
   - `/health/db` must execute a real database query.
   - `/health/redis` must execute a real Redis ping.
   - Do not return `"healthy"` for dependencies without probing them.

6. Webhook security must verify raw request bodies.
   - HMAC signatures are computed against the raw request body.
   - Never verify a signature against a re-serialized Pydantic model.
   - Missing or invalid signatures return `401`.

7. Configuration belongs in `app/core/config.py`.
   - Do not hard-code secrets, URLs, algorithms, or external service endpoints.
   - List-valued environment variables, such as `ALLOWED_ORIGINS`, must be JSON arrays.

8. Time values should be timezone-aware.
   - Use `datetime.now(UTC)` instead of `datetime.utcnow()`.
   - SQLAlchemy `DateTime` columns that represent instants should use `timezone=True`.

9. Tests must cover architectural boundaries.
   - Auth route tests should exercise register, login, refresh, and `/me`.
   - Health tests should cover process and database health.
   - Ingest tests should cover missing and valid webhook signatures.

## Service Pattern

Use this shape for new domain services:

```python
class ExampleService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def do_work(self, input_id: int) -> ExampleResponse:
        model = await self._load_model(input_id)
        if model is None:
            raise NotFoundError("Example was not found")
        return ExampleResponse.model_validate(model)
```

Route handlers should map service exceptions:

```python
@router.get("/{item_id}", response_model=ExampleResponse)
async def get_item(
    item_id: int,
    service: Annotated[ExampleService, Depends(get_example_service)],
) -> ExampleResponse:
    try:
        return await service.do_work(item_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
```

## Commands

```bash
# Create or reuse virtual environment
python -m venv .venv

# Install backend dependencies
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"

# Run tests
.\.venv\Scripts\python.exe -m pytest

# Quality checks
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m mypy app
```

If `uv` is available, prefer:

```bash
uv sync --extra dev
uv run pytest
uv run ruff check .
uv run mypy app
```

## Known Follow-Ups

- Add Alembic migration environment and first migration.
- Add Article, Source, Feed, and IngestJob models before implementing real ingestion.
- Add refresh-token persistence and revocation before production authentication.
- Add structured logging and request IDs before deployment.
