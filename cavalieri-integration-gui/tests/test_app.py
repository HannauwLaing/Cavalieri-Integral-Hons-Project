"""Standard Streamlit controls; custom JavaScript inputs are covered by Playwright."""
import ast
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

HOME = Path(__file__).resolve().parents[1] / "src" / "Home.py"


def two_d():
    app = AppTest.from_file(str(HOME), default_timeout=30).run()
    assert not app.exception
    app.switch_page("pages/Display_2D.py").run()
    assert not app.exception
    return app


def test_home_loads_and_renders_comparison_plots():
    app = AppTest.from_file(str(HOME), default_timeout=30).run()
    assert not app.exception
    assert len(app.get("plotly_chart")) >= 1


@pytest.mark.parametrize("page", ["pages/Display_2D.py", "pages/Display_3D.py"])
def test_pages_load(page):
    app = AppTest.from_file(str(HOME), default_timeout=30).run()
    app.switch_page(page).run()
    assert not app.exception
    assert any(button.label == "Generate" for button in app.button)


def test_configuration_controls_preserve_values():
    app = two_d()
    app.number_input(key="cfg2d_x_res").set_value(50).run()
    app.number_input(key="cfg2d_interm_cs").set_value(0).run()
    assert not app.exception
    assert app.number_input(key="cfg2d_x_res").value == 50
    assert app.number_input(key="cfg2d_interm_cs").value == 0


def test_invalid_interval_then_recovery():
    app = two_d()
    app.text_area(key="x_interval_text_box_Cav").set_value("not an interval").run()
    assert not app.exception
    assert app.warning
    app.text_area(key="x_interval_text_box_Cav").set_value("[0,2]").run()
    assert not app.exception
    assert ast.literal_eval(app.session_state["x_intervals_input_Cav"]) == [0, 2]


def test_add_and_remove_slider_after_multiple_text_intervals():
    app = two_d()
    app.text_area(key="x_interval_text_box_QuS").set_value("[0.0,0.5],[0.5,1.0]").run()
    selector = next(w for w in app.get("button_group") if w.key == "segment_QuS")
    selector.set_value("Sliders").run()
    assert not app.exception
    assert len(app.session_state["slider_QuS"]) == 2
    app.button(key="button_add_slider_QuS").click().run()
    assert not app.exception
    assert len(app.session_state["slider_QuS"]) == 3
    app.button(key="button_rem_slider_QuS").click().run()
    assert not app.exception
    assert len(app.session_state["slider_QuS"]) == 2

