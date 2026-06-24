# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Dev server
./manage.py runserver 0.0.0.0:8000
# Or via Docker Compose
docker compose up web

# Tests
py.test                                              # all tests (local)
py.test apps/blog/tests/queries_test.py              # single file
py.test apps/blog/tests/queries_test.py::TestBlogQuery::test_blog_query  # single test
py.test --reuse-db                                   # reuse test database

# Lint & type check
ruff check ./
ruff format ./
pyright
pre-commit run --all-files

# Migrations
./manage.py makemigrations
./manage.py migrate
./manage.py makemigrations --check --dry-run         # validate in CI

# Export GraphQL schema
./manage.py graphql_schema --out schema.graphql

# Shell
./manage.py shell_plus
```

**Package manager:** `uv` (not pip). **Python version:** 3.13.2 (see `.python-version`).

## Environment

Copy `.env` and fill in values. Key variables:

| Variable | Purpose |
|---|---|
| `DJANGO_SECRET_KEY` | Django secret key |
| `POSTGRES_DB/USER/PASSWORD/HOST/PORT` | Database connection |
| `FRONTEND_DOMAIN` | CORS allowed origin (e.g. `http://localhost:3055`) |
| `APP_DOMAIN` | Backend URL |
| `DEBUG` | Enable debug mode |
| `AWS_S3_ENABLED` | Use S3 for storage (false = local filesystem) |

## Architecture

### Django Apps (`apps/`)

| App | Purpose |
|---|---|
| `common` | Base models (`UserResource`, `StatusEnum`), serializers, admin, auth |
| `blog` | Blog posts |
| `news` | News articles |
| `department` | Organizational departments |
| `strategic` | Strategic directives and planning |
| `procurement` | Procurement/tenders |
| `vacancy` | Job vacancies |
| `project` | Projects |
| `faq` | Frequently asked questions |
| `resources` | Downloadable resources |
| `partner` | Partners/stakeholders |
| `radio_program` | Radio programs/media |
| `home` | Homepage content |

### GraphQL Setup

- **Library:** Strawberry GraphQL + `strawberry-graphql-django`
- **Endpoint:** `POST /graphql/` (CSRF-exempt)
- **GraphiQL:** `GET /graphiql/` (DEBUG mode only)
- **Main schema:** `main/graphql/schema.py` — aggregates `Query` and `Mutation` classes from every app
- **Context:** `main/graphql/context.py` — provides `info.context.request` and `info.context.dl` (data loaders)
- **Permissions:** `IsAuthenticated` from `strawberry_django.permissions` — apply via `extensions=[IsAuthenticated()]`

Each app's GraphQL code lives under `apps/<app>/graphql/`:
```
types.py      — @strawberry_django.type() declarations
queries.py    — Query class with offset_paginated / field resolvers
mutations.py  — Mutation class (create/update/delete)
inputs.py     — @strawberry_django.input() and @strawberry_django.partial() input types
filters.py    — @strawberry_django.filters.filter() for query filtering
orders.py     — @strawberry_django.ordering.order() for sorting
```

### Base Model Pattern

All content models inherit from `UserResource` (`apps/common/models.py`):

```python
class UserResource(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, ...)
    modified_by = models.ForeignKey(User, ...)

    class Meta:
        abstract = True
        ordering = ["-id"]
```

`created_by` / `modified_by` are auto-set by `UserResourceSerializer` — never set them manually.

**Status enum** (shared across all content models): `DRAFT=50`, `PUBLISHED=60`, `ARCHIVED=70`.

### Mutation Pattern

Mutations use `ModelMutation` from `utils/graphql/mutations.py` which delegates to DRF serializers:

```python
@strawberry_django.mutation(extensions=[IsAuthenticated()])
async def create_blog(self, info: Info, data: BlogCreateInput) -> MutationResponseType[BlogType]:
    return await ModelMutation(BlogSerializer).handle_create_mutation(data, info, None)

@strawberry_django.mutation(extensions=[IsAuthenticated()])
async def update_blog(self, info: Info, data: BlogUpdateInput, pk: strawberry.ID) -> MutationResponseType[BlogType]:
    blog = await Blog.objects.aget(pk=pk)
    return await ModelMutation(BlogSerializer).handle_update_mutation(data, info, blog)
```

All mutations return `MutationResponseType[T]` — a generic wrapper with `ok: bool`, `errors`, and `result: T`.

Delete mutations use `strawberry_django.mutations.delete()` with `key_attr="pk"`.

### Serializer Pattern

Content serializers extend `UserResourceSerializer` (`apps/common/serializers.py`), which auto-injects `created_by`/`modified_by` from `request.user`:

```python
class BlogSerializer(UserResourceSerializer):
    class Meta:
        model = Blog
        fields = ["id", "title", "published_date", "content", ...]
```

### Testing Pattern

Tests extend `main.tests.base_test.TestCase`, which provides:

- `self.query_check(query, variables, files, assert_errors)` — fires a POST to `/graphql/` and returns `response.json()`
- `self.assertResponseNoErrors(resp)` / `self.assertResponseHasErrors(resp)`
- Helpers: `self.genum()`, `self.gID()`, `self.g_pagination()`, `self.g_mutation_response()`
- Settings override: `DEBUG=True`, file-system storage, `CELERY_TASK_ALWAYS_EAGER=True`

Use `factory-boy` (`DjangoModelFactory`) for test fixtures. Factory files live at `apps/<app>/tests/factory.py`.

Test files follow: `apps/<app>/tests/queries_test.py` and `apps/<app>/tests/mutations_test.py`.

### Adding a New App

1. Create `apps/<app>/` with `models.py`, `serializers.py`, `admin.py`, `migrations/`
2. Create `apps/<app>/graphql/` with `types.py`, `queries.py`, `mutations.py`, `inputs.py`, `filters.py`, `orders.py`
3. Add to `INSTALLED_APPS` in `main/settings.py`
4. Add `Query` and `Mutation` to the aggregate schema in `main/graphql/schema.py`
5. Export schema: `./manage.py graphql_schema --out schema.graphql`

### Key Utilities

| Path | Purpose |
|---|---|
| `utils/graphql/mutations.py` | `ModelMutation` — generic create/update via DRF serializer |
| `utils/graphql/types.py` | `MutationResponseType`, `DjangoFileType`, `CudInput`, `DeleteInput` |
| `utils/graphql/common.py` | `parse_input_data()` — converts Strawberry input dataclass → dict |
| `utils/common.py` | `unique_slugify()`, `validate_file_size()`, `clean_up_none_keys()` |
| `main/graphql/enums.py` | `AppEnumCollection` — exposes all enums to GraphQL clients |
