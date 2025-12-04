FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y --no-install-recommends \
    gettext \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -r app && useradd -r -g app -m app

ENV APP_DIR=/usr/src/requests_app
RUN mkdir -p $APP_DIR
RUN mkdir $APP_DIR/staticfiles

WORKDIR $APP_DIR

RUN pip install uv

# Copy dependency files first for better layer caching
COPY pyproject.toml uv.lock ./

# Install dependencies (--frozen ensures lock file is used)
RUN uv sync --frozen

# Copy rest of application
COPY requests_app/ .

RUN chown -R app:app $APP_DIR

# Switch to non-root user
USER app

# Set uv cache directory to app-owned location
ENV UV_CACHE_DIR=$APP_DIR/.cache/uv

EXPOSE 8000

RUN chmod +x ./entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
