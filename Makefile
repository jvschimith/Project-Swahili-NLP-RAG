.PHONY: install init-db seed-data run-api run-streamlit run-tests

PYTHON ?= python3
PIP := $(PYTHON) -m pip

install:
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

init-db:
	$(PYTHON) -c "from src.infrastructure.database import init_db; init_db()"

seed-data:
	$(PYTHON) scripts/seed_release1_alpha.py

run-api:
	$(PYTHON) -m uvicorn src.web.api:app --reload --host 0.0.0.0 --port 8000

run-streamlit:
	$(PYTHON) -m streamlit run streamlit_app.py

run-tests:
	$(PYTHON) -m pytest
