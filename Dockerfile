FROM python:3.10-slim AS base
ENV POETRY_HOME="/opt/poetry" \
    PYTHONUNBUFFERED=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    PATH="/root/local/bin:$PATH"

WORKDIR /app
RUN pip install poetry==1.2.1
COPY pyproject.toml poetry.lock ./

FROM base AS local
RUN poetry install -n --no-root

FROM base AS production
RUN poetry install -n --no-dev --no-root
CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
