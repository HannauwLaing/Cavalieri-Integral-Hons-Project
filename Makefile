# Makefile (repo root)
# SHELL := /usr/bin/env zsh
# .ONESHELL:
# .SHELLFLAGS := -eu -o pipefail -c

VENV_DIR ?= .venv

BACKEND_DIR ?= rust-cavalieri-integration
GUI_DIR ?= cavalieri-integration-gui

PYTHON_SYS := python3

# APP ?= $(GUI_DIR)/src/Home.py

.PHONY: help venv backend gui setup run clean test-setup test test-backend test-python test-qs test-e2e test-monkey test-stress


DEBUG ?= 0
ifeq ($(DEBUG), 1)
    OUT := /dev/stdout
else
    OUT := /dev/null
endif


help:
	@echo "Targets:"
	@echo "  make all     - runs all setup and initiation and opens the server for the web application"
	@echo "  make setup   - Build & install Rust backend into venv"
	@# @echo "  make startup - Install GUI deps"
	@echo "  make run     - Run Streamlit from gui"
	@echo "               - Requirse <*make setup* to have been run>"
	@echo "               - On first running automaticly installs dependents for frontend"
	@echo "  make open    - Opens the browser on the "
	@echo "  make clean   - Removes generatod files"
	@echo "  make test-setup - Install test dependencies and Chromium (after make setup)"
	@echo "  make test        - Run all Rust, Python binding, and Streamlit AppTest tests"
	@echo ""
	@echo "use 'make <arg> DEBUG=1' to run with debug flags"

all: setup run
	@echo "[MAIN] Finished"
	# ./scripts/build.sh $(DEBUG)


# Set redirection target based on DEBUG value
	

setup:
	@echo "[MAIN] Calling Backend Makefile"
	@$(MAKE) -C $(BACKEND_DIR) all VENV_DIR=../$(VENV_DIR) PYTHON_SYS=$(PYTHON_SYS)  DEBUG=$(DEBUG) -s

run:
	@echo "[MAIN] Calling Frontend Makefile"
	@$(MAKE) -C $(GUI_DIR) run VENV_DIR=../$(VENV_DIR) PYTHON_SYS=$(PYTHON_SYS)  DEBUG=$(DEBUG) -s
open: 
	@echo "[MAIN] Calling Frontend Makefile"
	@$(MAKE) -C $(GUI_DIR) open VENV_DIR=../$(VENV_DIR) PYTHON_SYS=$(PYTHON_SYS)  DEBUG=$(DEBUG) -s

clean:
	@echo "[MAIN] Cleaning generated files"
	@$(MAKE) -C $(BACKEND_DIR) clean VENV_DIR=../$(VENV_DIR) PYTHON_SYS=$(PYTHON_SYS)  DEBUG=$(DEBUG) -s
	@$(MAKE) -C $(GUI_DIR) clean VENV_DIR=../$(VENV_DIR) PYTHON_SYS=$(PYTHON_SYS)  DEBUG=$(DEBUG) -s
	@# @rm -rf "$(VENV_DIR)"

test-setup:
	@$(MAKE) -C $(GUI_DIR) test-setup VENV_DIR=../$(VENV_DIR)

test: test-backend test-python
	@#;

test-backend:
	@$(MAKE) -C $(BACKEND_DIR) test

test-python:
	@$(MAKE) -C $(GUI_DIR) test VENV_DIR=../$(VENV_DIR)

