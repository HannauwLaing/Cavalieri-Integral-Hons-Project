
# Cavalieri Integration GUI

A Streamlit frontend for the local [Rust backend](../rust-cavalieri-integration/README.md), with interactive 2D and 3D visualizations, Riemann–Stieltjes and quadrilateral-strip comparisons, and STL export support for 3D models.

## Setup with Make

Follow the [root prerequisites](../README.md#prerequisites), then build the backend first. From the repository root:

```bash
make setup
cd cavalieri-integration-gui
make run
```

`make run` installs `requirements.txt` into the shared `../.venv/` and starts `src/Home.py` in headless mode. Open the URL printed in the terminal (normally `http://localhost:8501`) and use the sidebar to navigate to the 2D and 3D pages. Stop the server with `Ctrl+C`.

No environment activation is required. To build and launch everything from the repository root, use `make all` there.

## Frontend Makefile commands

Run these from `cavalieri-integration-gui/`:

| Command | Action |
| --- | --- |
| `make` / `make all` / `make run` | Install GUI requirements and start Streamlit with `--server.headless true`. |
| `make help` | Show available commands. |
| `make venv` | Create the shared environment if absent and upgrade pip, setuptools, and wheel. |
| `make deps` | Set up the environment and install `requirements.txt`. |
| `make open` | Install dependencies and start Streamlit without forcing headless mode. |
| `make clean` | Delete the shared `../.venv/`, including the installed backend. |

Both launch targets run in the foreground and check/install requirements every time. `make open` starts a server; it does not just open an existing instance's browser tab. Browser opening depends on the local Streamlit environment.

Use `make run DEBUG=1` to expose dependency-installation output. Override the entry point with `APP`, for example `make run APP=src/pages/Display_2D.py`. If overriding `VENV_DIR`, use the same environment as the backend.

## Direct commands

After installing the backend using its Makefile or direct setup instructions, run these from `cavalieri-integration-gui/`:

```bash
../.venv/bin/python -m pip install -r requirements.txt
../.venv/bin/python -m streamlit run src/Home.py --server.headless true
```

Omit `--server.headless true` to match `make open`. To use a different port:

```bash
../.venv/bin/python -m streamlit run src/Home.py --server.headless true --server.port 8502
```

## Tests

After building the backend, run `make test-setup` once. `make test` checks Python
bindings and Streamlit state; `make test-e2e` and `make test-monkey` exercise the real
math widget and browser. Tests manage their own server. Replay a sequence with
`make test-monkey MONKEY_SEEDS=3 MONKEY_STEPS=50`; logs, traces, and action histories
are in `test-results/`. The known 3D-to-2D sidebar JavaScript redeclaration error is
a strict expected failure; use `make test-e2e TEST_ARGS=--runxfail` to expose it.

## Troubleshooting

- **Backend import errors:** run `make -C ../rust-cavalieri-integration install DEBUG=1`, then restart the GUI. Although `requirements.txt` includes `cavint==1.0.4`, the GUI needs functions from this repository, so installing requirements alone is not a substitute for building the local backend.
- **Rust changes do not appear:** rebuild the backend and restart Streamlit.
- **Dependency installation fails:** run `make deps DEBUG=1` or the direct pip command to see the error.
- **Port already in use:** stop the previous server or choose another port with the direct command above.
- **After `make clean`:** build the backend again before launching, because the shared environment was removed.

Frontend `make venv` and `make deps` do not build the local Rust extension. See [LICENSE](LICENSE) for the frontend license.
