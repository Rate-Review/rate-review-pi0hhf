# Use a multi-stage build to reduce the final image size
# First stage: Build dependencies and application
FROM python:3.11-alpine AS builder

# Install system dependencies required for Poetry and dependencies
RUN apk add --no-cache --virtual .build-deps \
    build-base \
    postgresql-dev \
    libffi-dev \
    openssl-dev \
    python3-dev \
    musl-dev \
    zlib-dev \
    jpeg-dev \
    freetype-dev \
    lcms2-dev \
    openjpeg-dev \
    && pip install --upgrade pip

# Set working directory
WORKDIR /app

# Copy dependency files
COPY ./backend/pyproject.toml ./backend/poetry.lock ./

# Install Poetry
RUN pip install poetry==1.4.2

# Install Python dependencies using Poetry
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

# Copy application code
COPY ./backend .

# Set permissions for non-root user
RUN adduser -D appuser
RUN chown -R appuser:appuser /app

# Second stage: Create the runtime image
FROM python:3.11-alpine

# Install runtime dependencies
RUN apk add --no-cache postgresql-libs libffi openssl zlib jpeg freetype lcms2 openjpeg

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV FLASK_ENV=production

# Set working directory
WORKDIR /app

# Copy installed Python packages from the builder stage
COPY --from=builder /app/.venv ./.venv
COPY --from=builder /app .

# Create and switch to non-root user
RUN adduser -D appuser
USER appuser

# Expose the application port
EXPOSE 8000

# Define the entry point using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--threads", "2", "wsgi:application"]