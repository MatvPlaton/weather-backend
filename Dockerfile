FROM python:3.12-slim-bullseye AS builder

RUN pip install --no-cache-dir poetry==2.1.2

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache
   
WORKDIR /app
    
COPY pyproject.toml poetry.lock ./
    
RUN touch README.md
RUN poetry install --without dev --no-root && rm -rf $POETRY_CACHE_DIR
    

FROM python:3.12-slim-bullseye
    
ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

RUN useradd --create-home appuser

RUN chown -R appuser:appuser /app

USER appuser

COPY . .

EXPOSE 8080
    
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
