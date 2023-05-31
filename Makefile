SHELL := /bin/bash

run:
	docker compose -f ./docker-compose.dev.yaml up

build:
	docker build . -t zexxonn/translation:0.0.1 -f ./Dockerfile

run_local_api:
	ENV=test poetry run uvicorn src.api.main:app --host=0.0.0.0 --reload

stats:
	cloc $(git ls-files)
