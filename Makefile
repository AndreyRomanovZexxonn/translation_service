SHELL := /bin/bash

run_env_dev:
	docker compose -f ./docker-compose.dev.yaml up -Vd

run_env_test:
	docker compose -f ./docker-compose.test.yaml up -Vd

build:
	docker build . -t zexxonn/translation:0.0.1 -f ./Dockerfile

run_local_api:
	ENV=test poetry run uvicorn src.api.main:app --host=0.0.0.0 --reload

stats:
	cloc $(git ls-files)

test:
	poetry run pytest -vvv -s

