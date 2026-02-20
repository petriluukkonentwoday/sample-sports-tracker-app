# Sports Tracker Backend Dockerfile

FROM python:3.11-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy project files for dependency resolution
COPY pyproject.toml uv.lock* ./

# Install dependencies using uv
RUN uv sync --frozen --no-dev --no-install-project

# Copy application code
COPY . .

# Install the project
RUN uv sync --frozen --no-dev

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health')" || exit 1

# Run application using uv
CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
