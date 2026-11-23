use cavint::cav2d::display::{gen_display_cav, gen_display_rs, DisplayConfig2D};
use cavint::core::{differentiable::AD, integrate::gauss_kronrod_quadrature};

fn config() -> DisplayConfig2D {
    DisplayConfig2D {
        compute_integ: true,
        x_res: 50,
        y_res: 10,
        interm_cs: 2,
        max_rf_iters: 100,
        max_int_iters: 100,
        tol: 1e-9,
    }
}
fn close(actual: f64, expected: f64) {
    assert!(actual.is_finite());
    assert!(
        (actual - expected).abs() < 1e-8 + 1e-9 * expected.abs(),
        "{actual} != {expected}"
    );
}

#[test]
fn riemann_polynomials_and_orientation() {
    for degree in 0..=5 {
        for (a, b) in [(0., 1.), (1., 0.), (-1., 1.), (0.5, 0.5)] {
            let (actual, _) =
                gauss_kronrod_quadrature(|x| x.powi(degree), a, b, 1e-9, Some(100)).unwrap();
            close(
                actual,
                (b.powi(degree + 1) - a.powi(degree + 1)) / (degree + 1) as f64,
            );
        }
    }
}

#[test]
fn stieltjes_identity_and_polynomial_integrators() {
    for (g, expected) in [(0, 0.5), (1, 2. / 3.), (2, -0.5)] {
        let ds = gen_display_rs(
            &|x: AD| x,
            &|x: AD| match g {
                0 => x,
                1 => x.powi(2),
                _ => -x,
            },
            vec![[0., 1.]],
            config(),
        )
        .unwrap();
        close(ds.iter().map(|d| d.integ_value.unwrap().0).sum(), expected);
    }
}

#[test]
fn cavalieri_zero_and_nonzero_deformation() {
    // f=x+1, c(y)=-y gives g=x+f(x), hence integral f*g'=3.
    for (deform, expected) in [(false, 1.5), (true, 3.)] {
        let ds = gen_display_cav(
            &|x: AD| x + AD::from(1.),
            &|y: AD| if deform { -y } else { AD::from(0.) },
            vec![[0., 1.]],
            config(),
        )
        .unwrap();
        close(ds.iter().map(|d| d.integ_value.unwrap().0).sum(), expected);
    }
}
