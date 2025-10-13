# GitHire Backend Dockerfile
# Multi-stage build for optimal image size

# Stage 1: Base stage with Python dependencies
FROM python:3.11-slim AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Stage 2: Builder stage for installing Python packages
FROM base AS builder

# Copy pyproject.toml and source code for installation
COPY pyproject.toml ./
COPY src/ ./src/

# Install Python dependencies (regular install, not editable for Docker)
RUN pip install --user --no-warn-script-location .

# Stage 3: Final runtime stage
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/home/githire/.local/bin:$PATH

# Set working directory
WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security (do this early)
RUN useradd -m -u 1000 githire

# Copy Python packages from builder (includes installed dependencies)
COPY --from=builder --chown=githire:githire /root/.local /home/githire/.local

# Copy source code (needed for src.* imports)
COPY --chown=githire:githire src/ ./src/

# Copy config files needed at runtime
COPY --chown=githire:githire .env.example .env.example

# Create necessary directories
RUN mkdir -p /app/data /app/logs && \
    chown -R githire:githire /app

# Set PYTHONPATH so Python can find src modules
ENV PYTHONPATH=/app

# Switch to non-root user
USER githire

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["uvicorn", "src.backend_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
