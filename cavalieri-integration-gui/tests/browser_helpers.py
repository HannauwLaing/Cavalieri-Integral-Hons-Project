"""Selectors for the existing UI; no production test hooks are required."""
from playwright.sync_api import expect

MODES = ["Cavalieri Input", "Riemann-Stieltjes Input", "Quadrilateral Strips Input"]


def settle(page):
    # Component events are debounced; networkidle is inappropriate for Streamlit's
    # persistent websocket. Wait for the rerun indicator after the debounce.
    page.wait_for_timeout(200)
    expect(page.get_by_test_id("stApp")).to_have_attribute(
        "data-test-script-state", "notRunning", timeout=30000
    )
    expect(page.get_by_test_id("stStatusWidget")).not_to_be_visible(timeout=30000)


def healthy(page, errors):
    expect(page.get_by_test_id("stException")).to_have_count(0)
    assert not errors, f"Uncaught browser errors: {errors}"


def open_page(page, app_url, name="Display_2D"):
    page.goto(f"{app_url}/{name}" if name else app_url)
    expect(page.get_by_test_id("stAppViewContainer")).to_be_visible()
    if name == "Display_2D":
        expect(page.get_by_role("tab", name=MODES[0], exact=True)).to_be_visible()
    elif name == "Display_3D":
        expect(page.get_by_role("tab", name="Parameters", exact=True)).to_be_visible()
    else:
        expect(page.get_by_role("heading", name="Cavalieri Integration and Quadrilateral strips")).to_be_visible()
    settle(page)


def mode(page, name):
    page.get_by_role("tab", name=name, exact=True).click()
    settle(page)
    panel = page.get_by_role("tabpanel", name=name, exact=True)
    expect(panel).to_be_visible()
    return panel


def set_math(page, panel, index, expression):
    field = panel.frame_locator("iframe").nth(index).locator("math-field#mf")
    expect(field).to_be_visible()
    # Exercise the real component input listener and Streamlit postMessage bridge.
    # MathLive is a custom element, not an HTML input accepted by locator.fill().
    field.evaluate("""(element, value) => {
        element.value = value;
        element.dispatchEvent(new InputEvent('input', {bubbles: true, composed: true}));
    }""", expression)
    settle(page)
    expect(field).to_have_js_property("value", expression)


def set_auto(page, panel, enabled):
    auto = panel.get_by_label("Auto Generate", exact=True)
    # Streamlit's switch input is visually hidden under its clickable label.
    # Click the actual user-facing control instead of forcing a hidden-input click.
    if auto.is_checked() != enabled:
        panel.locator("label").filter(has_text="Auto Generate").click()
    expect(auto).to_be_checked(checked=enabled)
    settle(page)


def manual_mode(page, panel):
    set_auto(page, panel, False)


def generate(page, panel):
    manual_mode(page, panel)
    panel.get_by_role("button", name="Generate", exact=True).click()
    settle(page)


def no_calculation_error(page):
    expect(page.get_by_test_id("stAlert").filter(has_text="An error has occurred")).to_have_count(0)


def expect_plot(page):
    expect(page.get_by_test_id("stPlotlyChart").first).to_be_visible(timeout=30000)
