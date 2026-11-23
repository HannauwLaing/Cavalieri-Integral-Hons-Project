"""Seeded, bounded action sequences; replay with --monkey-seeds and --monkey-steps."""
import json
from pathlib import Path
import random

import pytest
from playwright.sync_api import expect

from .browser_helpers import (
    MODES, expect_plot, generate, healthy, manual_mode, mode,
    no_calculation_error, open_page, set_auto, set_math, settle,
)


@pytest.mark.monkey
@pytest.mark.timeout(600)
def test_seeded_frontend_actions(page, app_url, browser_errors, monkey_seed, request, output_path):
    rng = random.Random(monkey_seed)
    steps = request.config.getoption("--monkey-steps")
    assert steps > 0
    history = []
    artifact = Path(output_path) / "actions.json"
    artifact.parent.mkdir(parents=True, exist_ok=True)

    def record(action, **details):
        history.append({"step": len(history), "action": action, **details})
        artifact.write_text(json.dumps({"seed": monkey_seed, "steps": steps, "actions": history}, indent=2))

    open_page(page, app_url)
    current = MODES[2]
    panel = mode(page, current)
    # Weighted toward meaningful calculations, with bounded valid input families.
    actions = ["function", "function", "integrator", "interval", "generate",
               "mode", "config", "invalid_then_recover", "auto", "navigate"]
    try:
        for _ in range(steps):
            action = rng.choice(actions)
            if action == "mode":
                current = rng.choice(MODES)
                record(action, mode=current)
                panel = mode(page, current)
            elif action == "function":
                expression = rng.choice(["x+1", "2x+1", "x^2+1", r"\frac{x}{2}+1"])
                record(action, expression=expression, mode=current)
                manual_mode(page, panel)
                set_math(page, panel, 0, expression)
            elif action == "integrator":
                expression = rng.choice(["0", "-y"]) if current == MODES[0] else rng.choice(["x", "2x", "x^2"])
                record(action, expression=expression, mode=current)
                manual_mode(page, panel)
                set_math(page, panel, 1, expression)
            elif action == "interval":
                bounds = rng.choice(["[0,1]", "[0.1,0.8]", "[0,0.5],[0.5,1]"])
                record(action, bounds=bounds, mode=current)
                manual_mode(page, panel)
                panel.get_by_text("Text box", exact=True).click()
                settle(page)
                panel.locator("textarea").fill(bounds)
                panel.locator("textarea").press("Control+Enter")
                settle(page)
            elif action == "generate":
                record(action, mode=current)
                generate(page, panel)
                no_calculation_error(page)
                expect_plot(page)
            elif action == "config":
                curves = rng.choice([0, 1, 4, 10, 20])
                record(action, curves=curves)
                config = mode(page, "Config")
                entry = config.get_by_role("spinbutton", name="Intermediate Curves", exact=True)
                entry.fill(str(curves))
                entry.press("Enter")
                settle(page)
                expect(entry).to_have_value(str(curves))
                panel = mode(page, current)
            elif action == "invalid_then_recover":
                record(action, invalid="", replacement="x+1", mode=current)
                manual_mode(page, panel)
                set_math(page, panel, 0, "")
                generate(page, panel)
                expect(page.get_by_test_id("stAlert").filter(has_text="An error has occurred")).to_be_visible()
                healthy(page, browser_errors)
                set_math(page, panel, 0, "x+1")
                generate(page, panel)
                no_calculation_error(page)
                expect_plot(page)
            elif action == "auto":
                record(action, mode=current)
                set_auto(page, panel, True)
                expect(panel.get_by_role("button", name="Generate", exact=True)).to_be_disabled()
                no_calculation_error(page)
                expect_plot(page)
                manual_mode(page, panel)
            elif action == "navigate":
                destination = rng.choice(["", "Display_3D"])
                record(action, destination=destination)
                open_page(page, app_url, destination)
                healthy(page, browser_errors)
                open_page(page, app_url)
                panel = mode(page, current)
            healthy(page, browser_errors)
        # Every sequence must include a successful calculation, even for tiny runs.
        record("final_generate", mode=current)
        generate(page, panel)
        no_calculation_error(page)
        expect_plot(page)
        healthy(page, browser_errors)
    except Exception:
        page.screenshot(path=str(artifact.parent / "failure.png"), full_page=True)
        raise
