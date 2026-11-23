# Cavalieri Integration

An interactive sandbox for Cavalieri integration in two and three dimensions, Riemann–Stieltjes representations, and quadrilateral integration strips. A Rust calculation library exposes Python bindings to a Streamlit frontend.

## Prerequisites

The Makefiles target Debian/Ubuntu-style Linux systems: the backend checks dependencies using `dpkg` and offers to install missing packages with `sudo apt`. Install GNU Make, Python 3 with venv support, Rust (`rustc` and `cargo`), and a native compiler/linker:

```bash
sudo apt update
sudo apt install make build-essential python3 python3-venv rustc cargo
```

Setup requires internet access to download Python packages and Rust dependencies.

## Quick start

From the repository root:

```bash
make all
```

This creates the shared `.venv/`, builds and installs the local Rust backend, installs frontend requirements, and starts Streamlit in headless mode. Open the URL printed in the terminal (normally `http://localhost:8501`). Stop the server with `Ctrl+C`.

For subsequent launches, use `make run`. After changing Rust code, run `make setup` again and restart the app. Environment activation is optional: the Makefiles use `.venv/` directly.

## Root Makefile commands

| Command | Action |
| --- | --- |
| `make` / `make help` | Show the command summary. |
| `make all` | Set up the backend and launch the frontend. |
| `make setup` | Create/update the shared environment and build/install the backend. |
| `make run` | Install GUI dependencies and start Streamlit with `--server.headless true`. Run backend setup first. |
| `make open` | Install GUI dependencies and start Streamlit without forcing headless mode. Run backend setup first. |
| `make clean` | Delete backend `target/`, backend `Cargo.lock`, and the shared `.venv/`. |

`make open` starts a server; it does not just open a browser for an existing server. Browser opening depends on the local Streamlit environment. Both launch targets run in the foreground and check/install GUI requirements on every invocation.

## Troubleshooting

- **Setup fails without useful output:** repeat the target with `DEBUG=1`, for example `make all DEBUG=1`. Most setup output is hidden by default; the backend's Maturin pinning step remains silent even with this flag.
- **Missing backend imports:** run `make setup DEBUG=1` and restart the GUI. The frontend needs the local backend implementation.
- **Python compatibility errors:** inspect the build output. The backend uses older PyO3 and Maturin versions; its declared Python minimum does not guarantee compatibility with every interpreter or frontend dependency. Select an interpreter for a new environment with, for example, `make setup PYTHON_SYS=python3.12`. This does not change an existing environment's interpreter.
- **Resetting the environment:** stop the app, run `make clean`, then `make all`. This deletes installed packages and `Cargo.lock`; setup recreates the environment and resolves Rust dependencies again.

## Tests

After `make setup`, run `make test-setup` once. Use `make test` for Rust, Python
bindings, and Streamlit tests.

## Component guides

- [Backend README](rust-cavalieri-integration/README.md): Make targets, direct build commands, and library modules.
- [Frontend README](cavalieri-integration-gui/README.md): Make targets, direct launch commands, and troubleshooting.
