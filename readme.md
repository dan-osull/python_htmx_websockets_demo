Run (Docker):

    docker compose up -d

Run (Poetry):

    poetry run uvicorn src.main:app

Lint:

    poetry run black . && poetry run ruff . --fix