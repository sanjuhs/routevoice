SHELL := /bin/bash
PYTHON := .venv/bin/python
.PHONY: python tools test model-manifest physical
python:
	uv venv --python 3.12.13 .venv
	uv pip sync --python $(PYTHON) tools/requirements.lock
tools:
	./scripts/bootstrap.sh
test:
	$(PYTHON) -m unittest discover -s tests -v
model-manifest:
	$(PYTHON) scripts/export_model.py models/artifacts reports/tensor-manifest.json
physical:
	./scripts/run_physical.sh physical/die1.json
	./scripts/run_physical.sh physical/die2.json
	./scripts/run_physical.sh physical/die3.json
