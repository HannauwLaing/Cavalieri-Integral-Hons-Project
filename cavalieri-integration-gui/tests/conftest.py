"""Local backend checks and an isolated Streamlit server for browser tests."""
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
from urllib.error import URLError
from urllib.request import urlopen

import pytest

GUI = Path(__file__).resolve().parents[1]


def pytest_addoption(parser):
    parser.addoption("--monkey-seeds", default="0,1,2,3,4")
    parser.addoption("--monkey-steps", type=int, default=50)


def pytest_generate_tests(metafunc):
    if "monkey_seed" in metafunc.fixturenames:
        seeds = [int(s) for s in metafunc.config.getoption("--monkey-seeds").split(",")]
        metafunc.parametrize("monkey_seed", seeds, ids=lambda s: f"seed-{s}")


@pytest.fixture(scope="session", autouse=True)
def local_backend():
    import cavint
    assert callable(getattr(cavint, "display_cav2d_qs", None)), (
        "The local backend is required; run make setup from the repository root."
    )


@pytest.fixture(scope="session")
def app_url(pytestconfig):
    # Separate from any server the developer already has running.
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    artifacts = Path(pytestconfig.getoption("output"))
    artifacts.mkdir(parents=True, exist_ok=True)
    log_path = artifacts / "streamlit.log"
    env = {**os.environ, "PYTHONPATH": str(GUI / "src")}
    with log_path.open("w") as log:
        process = subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", "src/Home.py",
             "--server.address", "127.0.0.1", "--server.port", str(port),
             "--server.headless", "true", "--browser.gatherUsageStats", "false"],
            cwd=GUI, env=env, stdout=log, stderr=subprocess.STDOUT,
        )
        url = f"http://127.0.0.1:{port}"
        try:
            deadline = time.monotonic() + 30
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    pytest.fail(f"Streamlit exited. See {log_path}")
                try:
                    with urlopen(f"{url}/_stcore/health", timeout=1) as response:
                        if response.status == 200:
                            break
                except (URLError, TimeoutError):
                    time.sleep(0.1)
            else:
                pytest.fail(f"Streamlit did not become ready. See {log_path}")
            yield url
        finally:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


@pytest.fixture
def browser_errors(page):
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.set_default_timeout(15000)
    return errors
