SHELL := /bin/bash

run_test_api:
	ENV=test poetry run uvicorn src.api.main:app --host=0.0.0.0
