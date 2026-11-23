"""Exercise the actual installed PyO3 extension, including the LaTeX parser."""
import math
import time

import cavint
import pytest


def call(function, f="x+1", g="x", interval="[0,1]", **overrides):
    args = dict(compute_integ=True, x_res=32, y_res=12, interm_cs=3,
                max_rf_iters=100, max_int_iters=100, tol=1e-9)
    args.update(overrides)
    # Positional arguments also check the interface actually consumed by the GUI.
    return function(f, g, interval, *args.values())


def total(displays):
    assert displays
    for display in displays:
        value, error = display.integ_value
        assert math.isfinite(value)
        assert math.isfinite(error) and error >= 0
    return sum(d.integ_value[0] for d in displays)


@pytest.mark.parametrize("function,f,g,expected", [
    (cavint.display_cav2d, "x+1", "0", 1.5),
    (cavint.display_cav2d, "x+1", "-y", 3.0),
    (cavint.display_cav2d_rs, "x", "x", 0.5),
    (cavint.display_cav2d_rs, "x", "x^2", 2 / 3),
    (cavint.display_cav2d_rs, "x", "-x", -0.5),
])
def test_baseline_python_bindings(function, f, g, expected):
    assert total(call(function, f, g)) == pytest.approx(expected, abs=1e-8)


@pytest.mark.qs
@pytest.mark.parametrize("f,g,expected", [
    ("x^2", "x", 1 / 3), ("x", "2*x", 1),
    ("x^2", "2*x", 5 / 6), ("x", "0", 0),
    ("x", "x+2", 1.5), (r"\frac{x}{2}+1", "x", 1.25),
    (r"\sin(x)+2", "x", 3 - math.cos(1)),
    (r"\left(x+1\right)^2", "x", 7 / 3),
])
def test_qs_exact_latex_examples(f, g, expected):
    assert total(call(cavint.display_cav2d_qs, f, g)) == pytest.approx(expected, abs=1e-8)


@pytest.mark.qs
def test_qs_python_output_contract():
    displays = call(cavint.display_cav2d_qs, "x+1", "2*x")
    for d in displays:
        assert len(d.xv) == 33
        for name in ["fv", "gv", "dgv", "l1", "l2"]:
            values = getattr(d, name)
            assert len(values) == len(d.xv)
            assert all(math.isfinite(v) for v in values)
        assert len(d.cvs) == 5
        for index, curve in d.cvs:
            assert 0 <= index < len(d.xv)
            assert len(curve) == 13
            assert all(math.isfinite(v) for point in curve for v in point)
    assert total(displays) == pytest.approx(2.5)


@pytest.mark.qs
def test_qs_compute_disabled():
    assert all(d.integ_value is None for d in call(cavint.display_cav2d_qs, compute_integ=False))


@pytest.mark.parametrize("function", [cavint.display_cav2d, cavint.display_cav2d_rs, cavint.display_cav2d_qs])
@pytest.mark.parametrize("field,value", [("f", "unknownvariable"), ("interval", "not an interval")])
def test_invalid_text_is_a_python_exception(function, field, value):
    with pytest.raises(RuntimeError, match=".+"):
        call(function, **{field: value})


@pytest.mark.qs
def test_domain_error_is_a_python_exception():
    with pytest.raises(RuntimeError, match=".+"):
        call(cavint.display_cav2d_qs, r"\ln(x)", "x", "[-2,-1]")


def test_3d_binding_constant_triangle():
    ds = cavint.display_cav3d("2", "0", "0", "[[0,0],[0,1],[1,1]]", True, 5, 5, 5, 100, 1e-9)
    assert total(ds) == pytest.approx(1.0, abs=1e-8)
    assert len(ds) == 1


@pytest.mark.stress
@pytest.mark.timeout(60)
def test_qs_repeated_high_resolution_computation():
    start = time.monotonic()
    for _ in range(25):
        ds = call(cavint.display_cav2d_qs, "x^2+1", "2*x", x_res=500, y_res=500, interm_cs=20)
        assert total(ds) == pytest.approx(7 / 3, abs=1e-8)
    assert time.monotonic() - start < 60
