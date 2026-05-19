# PetCare MCP Server

Standalone MCP-oriented HTTP service for PetCare.

## What It Provides

- FastAPI HTTP endpoints for MCP-backed pet, document and clinic workflows
- PostgreSQL access through SQLAlchemy asyncio
- MinIO-backed document downloads
- Optional LLM adapters for assistant flows

## Local Setup

Install the project with development tooling:

```bash
pip install -e ".[dev]"
```

Run the local integration stack:

```bash
make up
```

Start the API directly:

```bash
make run
```

## Production Notes

In `production`, the service requires explicit values for:

- `POSTGRES_URL`
- `MINIO_ENDPOINT`
- `MINIO_ACCESS_KEY`
- `MINIO_SECRET_KEY`
- `MINIO_BUCKET_PRIVATE`
- `JWT_SECRET_KEY`
- `AUTH_DEMO_PASSWORD`
