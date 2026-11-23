# backend/Makefile
# SHELL := /usr/bin/env zsh
# .ONESHELL:
# .SHELLFLAGS := -eu -o pipefail -c


export PATH := $(HOME)/.cargo/bin:$(PATH)
VENV_DIR ?= ../.venv
PY := $(VENV_DIR)/bin/python
PIP := $(VENV_DIR)/bin/pip

PYTHON_SYS := python3

.PHONY: help all install build clean test test-qs test-stress

DEBUG ?= 0
ifeq ($(DEBUG), 1)
    OUT := /dev/stdout
else
    OUT := /dev/null
endif


all: install
	@echo "[RUST_BACKEND] Done"

help:
	@echo "Targets: (use make install)"
	@# @echo "  make deppendents - install all dependents needed for Backend"
	@echo "  make venv        - Create shared venv at $(VENV_DIR)"
	@echo "  make tools       - Install/upgrade build tools (pip, wheel, maturin)"
	@echo "  make install     - Build & install Rust backend into venv (maturin develop)"
	@echo "  make clean       - Remove build artifacts (not the venv)"
	@echo "  make test       - Run the complete Rust integration-test suite"
	@echo "  make test-qs    - Run quadrilateral-strip tests"
	@echo "  make test-stress - Run 4,096 cases for each quadrilateral property"
	@echo ""
	@echo "use 'make <arg> DEBUG=1' to run with debug flags"

_dependents:
	# sudo apt install rustc -y
	# sudo apt install cargo -y
	
	@set -e; \
	export PATH="$$HOME/.cargo/bin:$$PATH"; \
	MISSING=""; \
	if ! command -v curl >/dev/null 2>&1; then MISSING="$$MISSING curl"; fi; \
	if ! command -v $(PYTHON_SYS) >/dev/null 2>&1; then MISSING="$$MISSING $(PYTHON_SYS)"; fi; \
	for PKG in python3-venv build-essential pkg-config; do \
		if ! dpkg -s "$$PKG" >/dev/null 2>&1; then MISSING="$$MISSING $$PKG"; fi; \
	done; \
	RUSTUP_MISSING=0; \
	if ! command -v rustup >/dev/null 2>&1; then RUSTUP_MISSING=1; fi; \
	if [ -n "$$MISSING" ] || [ "$$RUSTUP_MISSING" -eq 1 ]; then \
		echo "[RUST_BACKEND] Missing dependencies:$$MISSING$$(if [ "$$RUSTUP_MISSING" -eq 1 ]; then printf ' rustup'; fi)"; \
		printf "[RUST_BACKEND] Install them now? [y/N]: "; \
		read ans || true; \
		if [ "$$ans" != "y" ] && [ "$$ans" != "Y" ]; then exit 1; fi; \
		if [ -n "$$MISSING" ]; then \
			sudo apt-get update > $(OUT) 2>&1; \
			sudo apt-get install -y $$MISSING > $(OUT) 2>&1; \
		fi; \
		if [ "$$RUSTUP_MISSING" -eq 1 ]; then \
			curl --proto '=https' --tlsv1.2 -fsSL https://sh.rustup.rs | sh -s -- -y > $(OUT) 2>&1; \
		fi; \
	fi; \
	export PATH="$$HOME/.cargo/bin:$$PATH"; \
	if ! command -v rustup >/dev/null 2>&1; then \
		echo "[RUST_BACKEND] rustup installation failed"; exit 1; \
	fi; \
	rustup default stable > $(OUT) 2>&1; \
	if ! rustc --version >/dev/null 2>&1 || ! cargo --version >/dev/null 2>&1; then \
		echo "[RUST_BACKEND] Repairing the Rust toolchain"; \
		rustup toolchain install stable --force > $(OUT) 2>&1; \
	fi; \
	if ! rustc --version >/dev/null 2>&1 || ! cargo --version >/dev/null 2>&1; then \
		echo "[RUST_BACKEND] Rust toolchain is not working"; exit 1; \
	fi; \
	echo "[RUST_BACKEND] Rust and system dependencies are ready"


venv: _dependents
	@echo "[RUST_BACKEND] Setting up the venv environment"
	@if [ ! -x "$(PY)" ] || ! "$(PY)" -m pip --version >/dev/null 2>&1; then \
		echo "[RUST_BACKEND] Creating or repairing the virtual environment"; \
		$(PYTHON_SYS) -m venv --clear "$(VENV_DIR)" > $(OUT) 2>&1 || exit 1; \
	fi
	@$(PY) -m pip install -U pip setuptools wheel > $(OUT) 2>&1

tools: venv
	@echo "[RUST_BACKEND] Installing correct dependensies"
	@$(PIP) install -U "maturin>=0.14,<0.15" > $(OUT) 2>&1

build: tools
	@echo "[RUST_BACKEND] Build the Rust wheel"
	@# @VIRTUAL_ENV="$(abspath $(VENV_DIR))" $(VENV_DIR)/bin/maturin build > $(OUT) 2>&1
	@$(VENV_DIR)/bin/maturin build > $(OUT) 2>&1
install: build
	@echo "[RUST_BACKEND] Install to the venv enviorment"
	@VIRTUAL_ENV="$(abspath $(VENV_DIR))" $(VENV_DIR)/bin/maturin develop > $(OUT) 2>&1

clean:
	@rm -rf ./target
	@rm -f ./Cargo.lock

_test_setup:
	@rustup component add llvm-tools-preview
	@cargo install cargo-llvm-cov

test: _test_setup
	cargo test --tests

test-qs: _test_setup
	cargo test --test quadrilateral_strips

test-stress: _test_setup
	PROPTEST_CASES=4096 cargo test --test quadrilateral_strips properties

test-coverage: _test_setup
	cargo llvm-cov --tests --html \
		--output-dir target/test-results/coverage

