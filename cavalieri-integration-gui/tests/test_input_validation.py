"""Run potentially unsafe native calls in child processes with a hard timeout.

Invalid configurations should raise a normal Python exception, never a Rust panic
or return a successful display. Subprocesses keep failures from killing pytest.
"""
import json
import subprocess
import sys

import pytest

CASES = [
    ("negative_tolerance", {"tol": -1.0}),
    ("zero_tolerance", {"tol": 0.0}),
    ("nan_tolerance", {"tol": float("nan")}),
    ("infinite_tolerance", {"tol": float("inf")}),
]

PROBE = """
import json, sys
from cavint import display_cav2d_qs
cfg = dict(compute_integ=True, x_res=8, y_res=4, interm_cs=2,
           max_rf_iters=10, max_int_iters=10, tol=1e-9)
cfg.update(json.loads(sys.argv[1]))
try:
    display_cav2d_qs('x+1', '2*x', '[0,1]', *cfg.values())
except (ValueError, RuntimeError):
    sys.exit(0)
sys.exit('Invalid configuration was accepted')
"""


@pytest.mark.qs
@pytest.mark.parametrize("name,overrides", CASES)
def test_invalid_configuration_is_rejected_without_panicking(name, overrides):
    completed = subprocess.run(
        [sys.executable, "-c", PROBE, json.dumps(overrides)],
        capture_output=True, text=True, timeout=10,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
