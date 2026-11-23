# gui/Makefile
# SHELL := /usr/bin/env zsh
# .ONESHELL:
# .SHELLFLAGS := -eu -o pipefail -c

VENV_DIR ?= ../.venv
PY := $(VENV_DIR)/bin/python
PIP := $(VENV_DIR)/bin/pip

# PYTHON_SYS := $(shell command -v python3.12 >/dev/null 2>&1 && echo python3.12 || echo python3)
PYTHON_SYS := python3

APP ?= src/Home.py #--global.developmentMode false

DEBUG ?= 0
ifeq ($(DEBUG), 1)
    OUT := /dev/stdout
else
    OUT := /dev/null
endif


.PHONY: help venv deps run open clean test-setup test test-qs test-e2e test-monkey test-stress

all: run
	@echo "Done"

help:
	@echo "Targets:"
	@echo "  make venv  - Create shared venv at $(VENV_DIR)"
	@echo "  make deps  - Install GUI deps from requirements.txt"
	@echo "  make run   - Run Streamlit (APP=$(APP)) without opening page"
	@echo "  make open  - Opens the page that the application runs on"
	@echo "  make clean - Remove venv (shared) if you want a full reset"
	@echo "  make test-setup - Install declared test requirements and Chromium"
	@echo "  make test       - Run binding and Streamlit AppTest coverage"
	@echo "  make test-qs    - Run focused quadrilateral binding tests"
	@echo "  make test-e2e   - Run fixed Chromium scenarios"
	@echo "  make test-monkey - Run seeded browser actions (MONKEY_SEEDS, MONKEY_STEPS)"
	@echo "  make test-stress - Run high-resolution and extended browser tests"

_checkVenv:
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "[PYTHON_FRONTEND] venv Directory is missing. Please run backend first."; \
		exit 0; \
	fi; \
	echo "[PYTHON_FRONTEND] Running" \


venv:
	@echo "[PYTHON_FRONTEND] Setting up the venv enviorment"
	@if [ ! -d "$(VENV_DIR)" ]; then \
		$(PYTHON_SYS) -m venv "$(VENV_DIR)" > $(OUT) 2>&1; \
	fi
	@$(PY) -m pip install -U pip setuptools wheel > $(OUT) 2>&1; \

deps: venv
	@echo "[PYTHON_FRONTEND] Installing correct dependensies"
	@$(PIP) install -r requirements.txt > $(OUT) 2>&1;

run: deps
	@echo "[PYTHON_FRONTEND] Running streamlit"
	@$(VENV_DIR)/bin/streamlit run $(APP) --server.headless true

open: deps
	@$(VENV_DIR)/bin/streamlit run $(APP)
	# xdg-open http://localhost:8501
clean:
	@rm -rf "$(VENV_DIR)"



#~~~~~~~~~~~~~~~~~~~`

PLAYWRIGHT_BROWSERS_PATH ?= $(abspath $(VENV_DIR))/playwright
export PLAYWRIGHT_BROWSERS_PATH
TEST_ARGS ?=
MONKEY_SEEDS ?= 0,1,2,3,4
MONKEY_STEPS ?= 50

test-setup:
	$(PY) -m pip install -r requirements.txt -r requirements-test.txt 
	$(PY) -m playwright install chromium

test:
	@$(PY) -m pytest tests -m "not e2e and not monkey and not stress" $(TEST_ARGS)

test-qs:
	@$(PY) -m pytest tests -m qs $(TEST_ARGS)

test-e2e:
	@$(PY) -m pytest tests -m e2e --output=test-results/e2e --tracing retain-on-failure --screenshot only-on-failure $(TEST_ARGS)

test-monkey:
	@$(PY) -m pytest tests -m monkey --output=test-results/monkey --monkey-seeds=$(MONKEY_SEEDS) --monkey-steps=$(MONKEY_STEPS) --tracing retain-on-failure --screenshot only-on-failure $(TEST_ARGS)

test-stress:
	@$(PY) -m pytest tests -m stress $(TEST_ARGS)
	@$(MAKE) test-monkey MONKEY_SEEDS=0,1,2,3,4,5,6,7,8,9 MONKEY_STEPS=200

test-coverage:
	# @$(PY) -m pytest tests 
	@$(PY) -m pytest tests -m "not monkey" \
		--cov=src/ \
		--cov-branch \
		--cov-report=term-missing \
		--cov-report=html:test-results/coverage \
		$(TEST_ARGS)
