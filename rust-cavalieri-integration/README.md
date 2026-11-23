# Rust Cavalieri Integration

A Rust library for Cavalieri integral visualizations in $\mathbb{R}^2$ and $\mathbb{R}^3$, Riemann–Stieltjes representations, and quadrilateral integration strips. PyO3 bindings expose the calculations to the [Streamlit frontend](../cavalieri-integration-gui/README.md).

## Setup with Make

See the [root prerequisites](../README.md#prerequisites) first. The dependency check uses Debian/Ubuntu's `dpkg` and can prompt to install missing packages through `sudo apt`.

From the repository root:

```bash
cd rust-cavalieri-integration
make install
```

This creates the shared `../.venv/`, installs build tools, builds a wheel, and installs the local extension with `maturin develop`. No environment activation is needed. Root `make setup` invokes this workflow too.

| Command | Action |
| --- | --- |
| `make` / `make all` / `make install` | Build and install the local backend. |
| `make help` | Show available commands. |
| `make venv` | Check system dependencies, create the environment if absent, and upgrade Python build tools. |
| `make tools` | Run environment setup and install `maturin>=0.14,<0.15`. |
| `make build` | Set up tools and build a wheel in `target/wheels/`; does not install it. |
| `make clean` | Delete `target/` and `Cargo.lock`; keep the shared environment. |

Use `make install DEBUG=1` to expose most build output. Re-run `make install` after changing Rust code, then restart the GUI to load the rebuilt extension. Builds use the default development profile.

`VENV_DIR` overrides the default `../.venv/`; the frontend must use the same environment. `PYTHON_SYS` selects the interpreter when creating an environment, for example `make install PYTHON_SYS=python3.12`.

## Direct commands

Run these from `rust-cavalieri-integration/` with the system prerequisites installed:

```bash
# Create the shared environment if it does not already exist.
python3 -m venv ../.venv
source ../.venv/bin/activate
python -m ensurepip --upgrade
python -m pip install --upgrade pip setuptools wheel 'maturin>=0.14,<0.15'

# Build a wheel and install the local extension for development.
maturin build
maturin develop

# Verify the functions used by the GUI can be imported.
python -c "from cavint import display_cav2d, display_cav2d_rs, display_cav2d_qs, display_cav3d; print('Backend imports OK')"
```

For an optimized wheel, use `maturin build --release`; output is in `target/wheels/`. To install an optimized local build, use `maturin develop --release`.

The Makefile pins Maturin to the 0.14 series, while `pyproject.toml` only specifies a lower bound. These direct commands follow the Makefile and expose errors hidden by its tool-installation step.

## Tests

Run `make test` for all Rust tests, `make test-qs` for quadrilateral strips, or
`make test-stress` for 4,096 cases per generated property. Quadrilateral tests use
exact antiderivatives, algebraic identities, and signed polygon-area convergence
as independent references. Cargo installs the declared dev-dependencies on first use.

## Modules

The library is partitioned into several functional modules, which can be accessed directly:

- `cav2d` - Cavalieri visualizations in $\mathbb{R}^2$ and Riemann-Stieltjes representations
- `cav3d` - Cavalieri visualization in $\mathbb{R}^3$
- `core`
    - `differentiable` - Forward mode Automatic Differentiation
    - `integrate` - 10-21 adaptive Gauss-Kronrod integration over intervals in $\mathbb{R}$ and triangles in $\mathbb{R}^2$
    - `triangulation` - Triangulation procedure for nested polygon sets
    - `parsing` - A parsing module for generating tree like representations of functions from text input.
- `pyo3_wrappers` - pyO3 wrapped functions for use with Python

## Using the Rust library locally

The crate produces both a Rust library and a Python extension named `cavint`. To use this checkout from another Rust project, add a path dependency:

```toml
[dependencies]
cavint = { path = "../rust-cavalieri-integration" }
```

Adjust the path relative to that project's `Cargo.toml`. See [LICENSE](LICENSE) for the backend license.
