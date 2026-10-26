# ==========================================
# Stage 1: Build & Dependency Resolution
# ==========================================
FROM python:3.13-slim-bookworm AS builder

# Copy uv executable from official uv image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Enable bytecode compilation and copy mode
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Step 1: Cache dependencies layer (only re-runs if dependencies change)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

# Step 2: Copy application code and install project
COPY . .
RUN uv sync --frozen --no-dev


# ==========================================
# Stage 2: Minimal Production Runtime
# ==========================================
FROM python:3.13-slim-bookworm AS runtime

# Install curl for container health check
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Security: Run as non-root user (Principle of Least Privilege)
RUN useradd -m -u 1000 appuser

WORKDIR /app

# Copy only the compiled virtualenv and application from the builder stage
COPY --from=builder --chown=appuser:appuser /app /app

# Configure environment variables
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Switch to non-root user
USER appuser

EXPOSE 8501

# Streamlit native health check endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

ENTRYPOINT ["streamlit", "run", "app.py"]
