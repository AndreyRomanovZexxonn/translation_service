FROM python:3.10.4-slim-buster
EXPOSE 8000

RUN apt-get update && \
    apt-get install -yqq --no-install-recommends build-essential python-dev && \
    rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir "poetry"

WORKDIR /app

COPY poetry.lock pyproject.toml /app/

RUN poetry export --without-hashes --format=requirements.txt > requirements.txt
RUN pip install -r requirements.txt

COPY src/ /app/src
COPY configs/ /app/configs

HEALTHCHECK --interval=1m CMD curl http://localhost:8000/api/healthcheck

CMD ["poetry", "run", "uvicorn", "src.api.main:app", "--host=0.0.0.0"]
