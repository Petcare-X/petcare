# Stage 1: Build
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1
# Copy only files needed for installation to cache layers
COPY pyproject.toml uv.lock ./
# Install dependencies into /app/.venv
RUN uv sync --frozen --no-install-project --no-dev

# Stage 2: Runtime
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

# Create a non-root user
RUN groupadd -r app && useradd -r -g app app

# Copy the virtual environment from the builder
COPY --from=builder /app/.venv /app/.venv

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_PROJECT_ENVIRONMENT="/app/.venv"

# Copy application code
COPY alembic.ini package.json pyproject.toml uv.lock ./
COPY alembic ./alembic
COPY src ./src

# Change ownership to non-root user
RUN chown -R app:app /app

# Switch to non-root user
USER app

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
