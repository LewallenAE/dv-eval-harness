FROM python:3.12-slim

# Create a non-root user early so we can set ownership in the same layer
RUN groupadd --system appuser && useradd --system --gid appuser --no-create-home appuser

WORKDIR /app

# Install dependencies before copying application code so this layer is
# cached as long as pyproject.toml hasn't changed.
COPY pyproject.toml README.md ./
RUN pip install --no-cache-dir -e .

# Copy application source.  mock_cases/ must land at /app/mock_cases/ to
# match the path resolution in app/main.py:
#   BACKEND_DIR = Path(__file__).resolve().parents[1]  →  /app
#   CASES_DIR   = BACKEND_DIR / "mock_cases"           →  /app/mock_cases
COPY app/ ./app/
COPY mock_cases/ ./mock_cases/

# Create the traces directory and hand ownership to appuser.
# The volume mount will overlay this at runtime, but the directory must
# exist with correct ownership for the case where no volume is attached.
RUN mkdir -p /app/traces && chown -R appuser:appuser /app/traces

# Switch to non-root user for all subsequent layers and the runtime process.
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
