SHELL := /bin/bash

run:
	docker compose -f ./docker-compose.dev.yaml up -Vd

build:
	docker build . -t zexxonn/translation:0.0.1 -f ./Dockerfile

test: run_docker_test
	poetry run pytest -vvv

stats:
	cloc $(git ls-files)

run_docker_test:
	docker compose -f ./docker-compose.test.yaml up -Vd

run_local_api: run_docker_test
	ENV=test poetry run uvicorn src.api.main:app --host=0.0.0.0 --reload
