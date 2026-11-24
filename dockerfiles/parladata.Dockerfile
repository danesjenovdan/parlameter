# we have to use python 3.8 since Lemmagen does not support 3.9
FROM python:3.14 AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y \
    libmemcached-dev \
    libsasl2-modules \
    gettext

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
	UV_LINK_MODE=copy \
	UV_PYTHON_DOWNLOADS=0 \
	UV_PROJECT_ENVIRONMENT=/opt/venv \
	PATH="/opt/venv/bin:$PATH" \
    DJANGO_SETTINGS_MODULE=parladata_project.settings.k8s \
	PYTHONUNBUFFERED=1

# Install dependencies first (cached separately from app code changes).
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
	uv sync --locked --no-dev --no-install-project

COPY . .

RUN --mount=type=cache,target=/root/.cache/uv \
	uv sync --locked --no-dev

EXPOSE 8000

RUN python3 manage.py compilemessages

FROM python:3.14 AS runtime

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y \
    libmemcached-dev \
    libsasl2-modules \
    gettext

EXPOSE 8000

WORKDIR /app

COPY --from=builder /app /app

ENV UV_PROJECT_ENVIRONMENT=/opt/venv \
	PATH="/opt/venv/bin:$PATH" \
	DJANGO_SETTINGS_MODULE=parladata_project.settings.k8s \
	PYTHONUNBUFFERED=1

COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /app /app

CMD exec python manage.py runserver 0.0.0.0:8000
