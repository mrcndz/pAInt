FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy shared package first
COPY libs/shared /shared
COPY libs/ai-service/pyproject.toml .

# Install shared package and dependencies
RUN pip install --no-cache-dir -e /shared
RUN pip install --no-cache-dir -e .

# Copy application code
COPY libs/ai-service .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8001

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]