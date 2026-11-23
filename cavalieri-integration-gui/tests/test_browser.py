import pytest
from playwright.sync_api import expect

from .browser_helpers import (
    MODES,
    expect_plot,
    generate,
    healthy,
    mode,
    no_calculation_error,
    open_page,
    set_math,
    settle,
)

pytestmark = pytest.mark.e2e


def test_home_comparison_plots(page, app_url, browser_errors):
    open_page(page, app_url, "")
    expect_plot(page)
    healthy(page, browser_errors)


@pytest.mark.parametrize("name", MODES)
def test_each_2d_mode_generates_plots(page, app_url, browser_errors, name):
    open_page(page, app_url)
    panel = mode(page, name)
    set_math(page, panel, 0, "x+1")
    set_math(page, panel, 1, "0" if name == MODES[0] else "2x")
    generate(page, panel)
    no_calculation_error(page)
    expect_plot(page)
    healthy(page, browser_errors)
    page.get_by_role("tab", name="Interval Integration Values", exact=True).click()
    expect(page.get_by_test_id("stDataFrame")).to_be_visible()


def test_invalid_expression_and_recovery(page, app_url, browser_errors):
    open_page(page, app_url)
    panel = mode(page, MODES[2])
    set_math(page, panel, 0, "")
    generate(page, panel)
    expect(
        page.get_by_test_id("stAlert").filter(has_text="An error has occurred")
    ).to_be_visible()
    healthy(page, browser_errors)
    set_math(page, panel, 0, "x+1")
    set_math(page, panel, 1, "x")
    generate(page, panel)
    no_calculation_error(page)
    expect_plot(page)
    healthy(page, browser_errors)


def test_math_keypad_and_keyboard(page, app_url, browser_errors):
    open_page(page, app_url)
    panel = mode(page, MODES[2])
    set_math(page, panel, 0, "")
    frame = panel.frame_locator("iframe").nth(0)
    frame.get_by_role("button", name="1", exact=True).click()
    settle(page)
    expect(frame.locator("math-field#mf")).to_have_js_property("value", "1")
    field = frame.locator("math-field#mf")
    field.click()
    field.press("End")
    field.press("+")
    field.press("x")
    settle(page)
    expect(field).to_have_js_property("value", "1+x")
    healthy(page, browser_errors)


def test_3d_default_generates(page, app_url, browser_errors):
    open_page(page, app_url, "Display_3D")
    panel = page.get_by_role("tabpanel", name="Parameters", exact=True)
    expect(
        panel.frame_locator("iframe").nth(0).locator("math-field#mf")
    ).to_be_visible()
    generate(page, panel)
    no_calculation_error(page)
    expect_plot(page)
    healthy(page, browser_errors)


def test_3d_test_2d_domain_plot(page, app_url, browser_errors):
    open_page(page, app_url, "Display_3D")
    text_box = page.get_by_role("radio", name="Text box")
    plane_2d = page.get_by_role("radio", name="2D-Plane")
    expect(text_box).to_be_visible()
    expect(plane_2d).to_be_visible()
    expect(text_box).to_have_attribute("aria-checked", "true")
    for _ in range(3):

        plane_2d.click()
        # expect(plane_2d).to_be_checked()
        expect(plane_2d).to_have_attribute("aria-checked", "true")

        text_box.click()
        expect(text_box).to_have_attribute("aria-checked", "true")
    healthy(page, browser_errors)


def test_3d_export_to_STL(page, app_url, browser_errors):
    open_page(page, app_url, "Display_3D")

    panel = page.get_by_role("tabpanel", name="Parameters", exact=True)

    expect(
        panel.frame_locator("iframe").nth(0).locator("math-field#mf")
    ).to_be_visible()

    generate(page, panel)
    no_calculation_error(page)
    expect_plot(page)

    download_button = page.get_by_role("button", name="Download STL File", exact=True)

    expect(download_button).to_be_visible()
    expect(download_button).to_be_enabled()
    with page.expect_download() as download_info:
        download_button.click()

    download = download_info.value
    assert download.suggested_filename.endswith(".stl")
    healthy(page, browser_errors)


class RedeclaredDocumentError(AssertionError):
    """Only the confirmed UI-001 error qualifies for the expected failure."""


@pytest.mark.known_bug
@pytest.mark.xfail(
    strict=True,
    raises=RedeclaredDocumentError,
    reason="UI-001: 3D to 2D navigation redeclares global const doc",
)
def test_sidebar_navigation_has_no_javascript_errors(page, app_url, browser_errors):
    open_page(page, app_url, "Display_3D")
    panel = page.get_by_role("tabpanel", name="Parameters", exact=True)
    expect(
        panel.frame_locator("iframe").nth(0).locator("math-field#mf")
    ).to_be_visible()
    generate(page, panel)
    no_calculation_error(page)
    expect_plot(page)
    healthy(page, browser_errors)
    page.get_by_role("link", name="Display 2D", exact=True).click()
    expect(page.get_by_role("tab", name=MODES[2], exact=True)).to_be_visible()
    settle(page)
    if browser_errors == [
        "Failed to execute 'replaceChild' on 'Node': Identifier 'doc' has already been declared"
    ]:
        raise RedeclaredDocumentError(browser_errors[0])
    healthy(page, browser_errors)
