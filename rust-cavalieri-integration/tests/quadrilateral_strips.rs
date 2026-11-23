//! Independent references: exact polynomial antiderivatives, endpoint identity,
//! and signed polygon areas. Never use the production quadrature as the oracle.
use cavint::cav2d::display::{gen_display_qs, DisplayConfig2D, QuadDisplay2D};
use cavint::core::differentiable::AD;
use proptest::prelude::*;

fn config() -> DisplayConfig2D {
    DisplayConfig2D {
        compute_integ: true,
        x_res: 64,
        y_res: 12,
        interm_cs: 4,
        max_rf_iters: 200,
        max_int_iters: 200,
        tol: 1e-9,
    }
}

fn poly(c: &[f64], x: AD) -> AD {
    c.iter()
        .rev()
        .fold(AD::from(0.0), |v, a| v * x + AD::from(*a))
}

fn value(c: &[f64], x: f64) -> f64 {
    c.iter().rev().fold(0.0, |v, a| v * x + a)
}

fn primitive(c: &[f64], x: f64) -> f64 {
    c.iter()
        .enumerate()
        .map(|(i, a)| a * x.powi(i as i32 + 1) / (i + 1) as f64)
        .sum()
}

fn reference(f: &[f64], g: &[f64], a: f64, b: f64) -> f64 {
    primitive(f, b) - primitive(f, a)
        + 0.5 * (value(f, b) * (value(g, b) - b) - value(f, a) * (value(g, a) - a))
}

fn close(actual: f64, expected: f64) {
    assert!(actual.is_finite(), "nonfinite result: {actual}");
    assert!(
        (actual - expected).abs() <= 2e-8 + 2e-9 * expected.abs(),
        "actual={actual:.16e}, expected={expected:.16e}"
    );
}

fn displays(
    f: &[f64],
    g: &[f64],
    intervals: Vec<[f64; 2]>,
    cfg: DisplayConfig2D,
) -> Vec<QuadDisplay2D> {
    gen_display_qs(&|x| poly(f, x), &|x| poly(g, x), intervals, cfg)
        .unwrap_or_else(|e| panic!("f={f:?}, g={g:?}: {e}"))
}

fn total(ds: &[QuadDisplay2D]) -> f64 {
    ds.iter()
        .map(|d| {
            let (v, error) = d.integ_value.expect("integration enabled");
            assert!(error.is_finite() && error >= 0.0);
            v
        })
        .sum()
}

macro_rules! polynomial_case {
    ($name:ident, $f:expr, $g:expr, $a:expr, $b:expr) => {
        #[test]
        fn $name() {
            let (f, g, a, b) = ($f, $g, $a, $b);
            let ds = displays(f, g, vec![[a, b]], config());
            assert!(!ds.is_empty());
            close(total(&ds), reference(f, g, a, b));
            close(ds.first().unwrap().a, a);
            close(ds.last().unwrap().b, b);
            for pair in ds.windows(2) {
                close(pair[0].b, pair[1].a);
            }
            for d in ds {
                close(d.integ_value.unwrap().0, reference(f, g, d.a, d.b));
            }
        }
    };
}

polynomial_case!(identity_quadratic, &[0., 0., 1.], &[0., 1.], 0., 1.);
polynomial_case!(identity_cubic, &[1., 0., 0., 1.], &[0., 1.], 0., 1.);
polynomial_case!(identity_quartic, &[1., 0., 0., 0., 1.], &[0., 1.], 0., 1.);
polynomial_case!(linear_doubled_base, &[0., 1.], &[0., 2.], 0., 1.);
polynomial_case!(quadratic_doubled_base, &[0., 0., 1.], &[0., 2.], 0., 1.);
polynomial_case!(constant_integrator, &[0., 1.], &[0.], 0., 1.);
polynomial_case!(translated_integrator, &[0., 1.], &[2., 1.], 0., 1.);
polynomial_case!(decreasing_integrator, &[1., 1.], &[0., -1.], 0., 1.);
polynomial_case!(negative_integrand, &[-2., -1.], &[0., 2.], 0., 1.);
polynomial_case!(zero_crossing, &[0., 1.], &[0., 2.], -1., 1.);
polynomial_case!(turning_integrand, &[1., 0., 1.], &[0., 1.], -1., 1.);
polynomial_case!(turning_integrator, &[2., 1.], &[0., 0., 1.], -1., 1.);
polynomial_case!(shared_turning_point, &[1., 0., 1.], &[0., 0., 1.], -1., 1.);
polynomial_case!(
    distinct_turning_points,
    &[2., 0., 1.],
    &[0., -1., 1.],
    -1.,
    1.
);
polynomial_case!(
    multiple_turning_points,
    &[3., -1., 0., 1.],
    &[0., 1.],
    -1.,
    1.
);
polynomial_case!(stationary_inflection, &[2., 0., 0., 1.], &[0., 2.], -1., 1.);
polynomial_case!(reverse_bounds, &[1., 0., 1.], &[0., 2.], 1., 0.);
polynomial_case!(
    reverse_across_turning_point,
    &[1., 0., 1.],
    &[0., 0., 1.],
    1.,
    -1.
);
polynomial_case!(negative_interval, &[0., 1.], &[1., 0., 1.], -2., -1.);
polynomial_case!(small_interval, &[1., 1.], &[0., 2.], 0.5, 0.50001);
polynomial_case!(large_scale, &[1e5, 1e5], &[0., 2.], 0., 1.);
polynomial_case!(small_scale, &[1e-4, 1e-4], &[0., 2.], 0., 1.);
polynomial_case!(constant_function, &[1.], &[0., 0., 1.], 0., 1.);
polynomial_case!(zero_function, &[0.], &[0., 1.], 0., 1.);
polynomial_case!(zero_length_interval, &[1., 1.], &[0., 2.], 0.5, 0.5);

#[test]
fn exact_examples_distinguish_quadrilateral_from_stieltjes() {
    close(
        total(&displays(
            &[0., 0., 1.],
            &[0., 2.],
            vec![[0., 1.]],
            config(),
        )),
        5. / 6.,
    );
    close(
        total(&displays(&[0., 1.], &[2., 1.], vec![[0., 1.]], config())),
        1.5,
    );
}

#[test]
fn interval_additivity_and_disjoint_intervals() {
    let (f, g) = (&[2., 1., 1.][..], &[1., 2.][..]);
    let whole = total(&displays(f, g, vec![[0., 1.]], config()));
    close(
        total(&displays(f, g, vec![[0., 0.3], [0.3, 1.]], config())),
        whole,
    );
    close(
        total(&displays(f, g, vec![[0., 0.2], [0.7, 1.]], config())),
        reference(f, g, 0., 0.2) + reference(f, g, 0.7, 1.),
    );
}

#[test]
fn integrators_with_same_endpoints_agree() {
    let f = &[1., 1., 1.];
    close(
        total(&displays(f, &[0., 1.], vec![[0., 1.]], config())),
        total(&displays(f, &[0., 0., 1.], vec![[0., 1.]], config())),
    );
}

#[test]
fn empty_interval_list_is_empty() {
    assert!(displays(&[1., 1.], &[0., 1.], vec![], config()).is_empty());
}

#[test]
fn disabled_integration_preserves_display_data() {
    let mut cfg = config();
    cfg.compute_integ = false;
    let ds = displays(&[1., 1.], &[0., 2.], vec![[0., 1.]], cfg);
    assert!(!ds.is_empty());
    assert!(ds
        .iter()
        .all(|d| d.integ_value.is_none() && !d.xv.is_empty()));
}

#[test]
fn display_shapes_endpoints_and_samples() {
    let ds = displays(&[1., 1.], &[0., 2.], vec![[0., 1.]], config());
    for d in ds {
        for arr in [&d.fv, &d.gv, &d.dgv, &d.l1, &d.l2] {
            assert_eq!(arr.len(), d.xv.len());
            assert!(arr.iter().all(|v| v.is_finite()));
        }
        assert_eq!(d.xv.len(), 65);
        assert_eq!(d.cvs.len(), 6);
        for (i, &x) in d.xv.iter().enumerate() {
            close(d.fv[i], 1. + x);
            close(d.dgv[i], 2.);
            close(d.l1[i], 0.5 + x);
            close(d.l2[i], 1. + x);
        }
        for (index, curve) in d.cvs {
            assert!(index < d.xv.len());
            assert_eq!(curve.len(), 13);
            assert!(curve.iter().flatten().all(|v| v.is_finite()));
            close(curve[0][0], 0.);
            close(curve[0][1], d.gv[index]);
            close(curve.last().unwrap()[0], d.fv[index]);
            close(curve.last().unwrap()[1], d.xv[index]);
        }
    }
}

#[test]
fn resolution_and_strip_count_do_not_change_integral() {
    for resolution in [1, 2, 16, 64] {
        for curves in [0, 1, 20] {
            let mut cfg = config();
            cfg.x_res = resolution;
            cfg.y_res = resolution;
            cfg.interm_cs = curves;
            let ds = displays(&[1., 1.], &[0., 2.], vec![[0., 1.]], cfg);
            close(total(&ds), 2.5);
            assert_eq!(ds[0].cvs.len(), curves + 2);
            assert!(ds[0].cvs.iter().all(|(i, _)| *i <= resolution));
        }
    }
}

#[test]
fn sine_function_matches_exact_primitive() {
    let ds = gen_display_qs(
        &|x: AD| x.sin() + AD::from(2.),
        &|x: AD| x * AD::from(2.),
        vec![[0., 1.]],
        config(),
    )
    .unwrap();
    close(total(&ds), 4. - 1f64.cos() + 0.5 * 1f64.sin());
}

#[test]
fn oscillatory_function_across_extrema() {
    let b = 2. * std::f64::consts::PI;
    let ds = gen_display_qs(
        &|x: AD| x.sin() + AD::from(2.),
        &|x: AD| x,
        vec![[0., b]],
        config(),
    )
    .unwrap();
    assert!(ds.len() > 1);
    close(total(&ds), 2. * b);
}

#[test]
fn invalid_function_domain_returns_error() {
    assert!(gen_display_qs(&|x: AD| x.ln(), &|x: AD| x, vec![[-2., -1.]], config()).is_err());
}

#[test]
fn integration_iteration_limit_returns_error() {
    let mut cfg = config();
    cfg.max_int_iters = 0;
    assert!(gen_display_qs(&|x: AD| x, &|x: AD| x, vec![[0., 1.]], cfg).is_err());
}

#[test]
fn root_iteration_limit_returns_error() {
    let mut cfg = config();
    cfg.max_rf_iters = 0;
    assert!(gen_display_qs(
        &|x: AD| x.powi(2) + AD::from(1.),
        &|x: AD| x * AD::from(2.),
        vec![[0., 1.]],
        cfg
    )
    .is_err());
}

// The shoelace oracle uses only strip vertices, not derivatives or quadrature.
fn polygon_sum(f: &[f64], g: &[f64], a: f64, b: f64, n: usize) -> f64 {
    (0..n)
        .map(|i| {
            let u = a + (b - a) * i as f64 / n as f64;
            let v = a + (b - a) * (i + 1) as f64 / n as f64;
            let p = [
                [value(g, u), 0.],
                [value(g, v), 0.],
                [v, value(f, v)],
                [u, value(f, u)],
            ];
            (0..4)
                .map(|j| p[j][0] * p[(j + 1) % 4][1] - p[(j + 1) % 4][0] * p[j][1])
                .sum::<f64>()
                / 2.
        })
        .sum()
}

#[test]
fn signed_polygon_areas_converge_to_integral() {
    for (a, b, sign) in [(0., 1., 1.), (1., 0., 1.), (0., 1., -1.)] {
        let (f, g) = (&[sign, 0., sign][..], &[0., 2.][..]);
        let expected = total(&displays(f, g, vec![[a, b]], config()));
        let coarse_error = (polygon_sum(f, g, a, b, 16) - expected).abs();
        let fine_error = (polygon_sum(f, g, a, b, 1024) - expected).abs();
        assert!(fine_error < coarse_error / 100.);
        assert!(fine_error < 1e-6);
    }
}

mod properties {
    use super::*;
    proptest! {
        // Positive derivative on [0, 1] keeps the display inverse well defined.
        // Nonmonotone cases have explicit deterministic tests above.
        #[test]
        fn polynomial_endpoint_identity(
            c in -4.0f64..4.0, slope in 0.5f64..4.0, quadratic in 0.0f64..2.0,
            g0 in -2.0f64..2.0, g1 in 0.5f64..3.0, g2 in 0.0f64..2.0,
            a in 0.0f64..0.4, b in 0.6f64..1.0,
        ) {
            let f = [c, slope, quadratic];
            let g = [g0, g1, g2];
            close(total(&displays(&f, &g, vec![[a, b]], config())), reference(&f, &g, a, b));
        }

        #[test]
        fn reversal_and_linearity(c in 1.0f64..3.0, slope in 0.5f64..3.0, scale in 0.5f64..3.0) {
            let f = [c, slope];
            let scaled = [scale * c, scale * slope];
            let g = [0., 2.];
            let q = total(&displays(&f, &g, vec![[0., 1.]], config()));
            close(total(&displays(&f, &g, vec![[1., 0.]], config())), -q);
            close(total(&displays(&scaled, &g, vec![[0., 1.]], config())), scale * q);
            let other = [2., 1.];
            let sum = [c + 2., slope + 1.];
            close(total(&displays(&sum, &g, vec![[0., 1.]], config())),
                q + total(&displays(&other, &g, vec![[0., 1.]], config())));
        }
    }
}
