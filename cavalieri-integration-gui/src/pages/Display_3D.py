import ast
import numpy as np

# from pandas._libs.lib import fast_multiget
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from cavint import display_cav3d
import streamlit as st
import pandas as pd

pd.set_option("display.float_format", "{:.3e}".format)

from PIL import Image, ImageDraw
from streamlit_image_coordinates import streamlit_image_coordinates

# from utils.Helper_Functions import latex_to_expr
from utils.Helper_Functions import is_float
from utils.math_component import math_input_component
from utils.export_to_stl import export_cav3d_displays_to_stl

DEBUG_FLAG = False


def dprint(*args, **kwargs):
    if DEBUG_FLAG:
        print(*args, **kwargs)


# NOTE: Done this demo
# Latex convertion
# Presets
# symble insert table
# Format domain text box
# *** 2D plain ***
# Auto generate
# 3D-printing
#
#


# TO-DO: 3D exponent in f(x,y) cant be negitive????
# TO-DO: implement Hide grid/axis
# TO-DO: make 3D printable export look nicer

# TO-DO: Implement a dark mode for the canvas

# TO-DO: make a "Fit grid to shape size" button
#               that scales the grid size to the current shape size + 25% each side

# NOTE: https://imagetostl.io/tools/stl-viewer
# TEST:
# \frac{\left(x^2+7+8-9+\pi+e+\ln(4)+\sqrt5\right)\left(\sin(1)+\cos(2)+\tan(3)+\sinh(02-\left(\left(x\cos\left(\pi\left(1-\left(x^{32}+y^{32}\right)^{\frac{1}{32}}\right)\right)+y\sin\left(\pi\left(1-\left(x^{32}+y^{32}\right)^{\frac{1}{32}}\right)\right)\right)^{32}+\left(-x\sin\left(\pi\left(1-\left(x^{32}+y^{32}\right)^{\frac{1}{32}}\right)\right)+y\cos\left(\pi\left(1-\left(x^{32}+y^{32}\right)^{\frac{1}{32}}\right)\right)\right)^{32}\right)^{\frac{1}{32}})

# 1-\left(\left(x\cos\left(2\pi\left(1-\sqrt{x^2+y^2}\right)\right)+y\sin\left(2\pi\left(1-\sqrt{x^2+y^2}\right)\right)\right)^{12}+\left(-y\cos\left(2\pi\left(1-\sqrt{x^2+y^2}\right)\right)+x\sin\left(2\pi\left(1-\sqrt{x^2+y^2}\right)\right)\right)^{12}\right)^{\frac{1}{12}}
# 1-\left(\left(x\cos\left(2\pi\left(1-\sqrt{x^2+y^2}\right)\right)+y\sin\left(2\pi\left(1-\sqrt{x^2+y^2}\right)\right)\right)^{12}+\left(-y\cos\left(2\pi\left(1-\sqrt{x^2+y^2}\right)\right)+x\sin\left(2\pi\left(1-\sqrt{x^2+y^2}\right)\right)\right)^{12}\right)^{\frac{1}{12}}

# 1-\left(\left(x\cos\left(\pi\left(1-\left(x^{32}+y^{32}\right)^{\frac{1}{32}}\right)\right)+y\sin\left(\pi\left(1-\left(x^{32}+y^{32}\right)^{\frac{1}{32}}\right)\right)\right)^{32}+\left(-x\sin\left(\pi\left(1-\left(x^{32}+y^{32}\right)^{\frac{1}{32}}\right)\right)+y\cos\left(\pi\left(1-\left(x^{32}+y^{32}\right)^{\frac{1}{32}}\right)\right)\right)^{32}\right)^{\frac{1}{32}}


# [[-1,-1],[-1,1],[1,1],[1,-1],[[-0.5, -0.5],[-0.5, 0.5],[0.5, 0.5],[0.5, -0.5]]
# [[-0.8,-0.8],[0.8,-0.8],[0.8,0.8],[-0.8,0.8]]


comments = [
    """ Helix:
f(x,y) =
2pi+x-y

c1(z) =
1-cos(z)

c2(z) =
sin(z)

S =
[[1,1],[1,2],[2,2],[2,1]]

""",
    """ Prismtiod:
f(x,y) =
-x-y+8

c1(z) =
\frac{z}{2}

c2(z) =
z

S =
[[1.6,3.2],[0.8,5.6],[4,4],[4.8,1.6]]

""",
]

dprint("~~~~~~~~~~~~~~~~~~Start of reload~~~~~~~~~~~~~~~~~~~")

st.markdown(
    """
<style>
div[data-testid="stExpander"] details {
    border: 0px !important;
    box-shadow: none !important;
    }
div[data-testid="stExpander"] details summary {
    display: none;
    border: 0px !important;
    box-shadow: none !important;
    }
div[data-testid="stAppDeployButton"] {
    display: none !important;
    }
}
</style>
""",
    unsafe_allow_html=True,
)

# ~~~~~~~~~~~~~~~~~~~ Ensure using theme change causes a rerun:

if st.button("ThemeChangedTriggerBtn", key="theme_change_trigger_btn"):
    # NOTE: Theme changing does not by default cause a rerun
    # This button just needs to be called to trigger a rerun
    # It is hidden but called when theme is changed
    pass
st.html(
    """
    <style> 
        .st-key-theme_change_trigger_btn {display: none !important;}
    </style>
    <script>
        const doc = window.parent.document;
        function applyThemeChangeTrigger() {
            ['System', 'Light', 'Dark'].forEach(theme => {
                const el = doc.querySelector(`[data-testid="stMainMenuItem-theme-${theme}"]`);
                if (el && !el.dataset.hasClickListener) {
                    el.dataset.hasClickListener = "true";
                    el.addEventListener('click', () => {
                        setTimeout(() => {
                            const syncBtn = Array.from(doc.querySelectorAll('button'))
                                                  .find(el => el.textContent === "ThemeChangedTriggerBtn");
                            // console.log(syncBtn);
                            if (syncBtn) {
                                syncBtn.click();
                            }
                        }, 100); 
                    });
                }
            });
        }
        const observer = new MutationObserver(() => {
            applyThemeChangeTrigger();
        });
        observer.observe(doc.body, { childList: true, subtree: true });
    </script>
""",
    unsafe_allow_javascript=True,
)

WIDTH, HEIGHT = 500, 500


def points_to_string(points):
    return (
        "[\n\t"
        + "\n],[\n\t".join(
            [
                ",\n\t".join(
                    ["[" + str(x) + "," + str(y) + "]" for (x, y) in arr_shape]
                )
                for arr_shape in points
            ]
        )
        + "\n]"
    )


def coord_to_canvas(x, y, width, height, x_max, y_max):

    px = (x - x_max[0]) / (x_max[1] - x_max[0]) * (width - 1)
    py = (y_max[1] - y) / (y_max[1] - y_max[0]) * (height - 1)

    # px = px * 0.96 + width  * 0.02
    # py = py * 0.96 + height * 0.02

    return int(round(px)), int(round(py))


def canvas_to_coord(px, py, width, height, x_max, y_max):
    # px = (px + width  * 0.02) / 0.96
    # py = (py + height * 0.02) / 0.96

    x = x_max[0] + px / (width - 1) * (x_max[1] - x_max[0])
    y = y_max[1] - py / (height - 1) * (y_max[1] - y_max[0])

    return x, y


def draw_default_image(draw, width, height, xlim, ylim, steps, hide_grid, hide_axis):
    current_theme = st.context.theme.type
    if current_theme == "light":
        pass
        colour_axis = "black"
        colour_grid = "lightgray"
        colour_text = "gray"

    else:
        colour_axis = "white"
        colour_grid = "gray"
        colour_text = "lightgray"
    arr_x = []
    arr_y = []
    # Lines at x=0 and y = 0
    x_center, y_center = coord_to_canvas(0, 0, width, height, xlim, ylim)
    if not hide_axis:
        draw.line([(x_center, 0), (x_center, height)], fill=colour_axis, width=2)
        draw.line([(0, y_center), (width, y_center)], fill=colour_axis, width=2)
    arr_x.append(x_center)
    arr_y.append(y_center)

    x_negitive = np.append(np.arange(0, xlim[0] - 1e-9, -steps), xlim[0])
    x_positive = np.append(np.arange(0, xlim[1] + 1e-9, steps), xlim[1])
    # Vertical lines
    for x in np.concatenate((x_negitive, x_positive)):

        px, _ = coord_to_canvas(x, 0, width, height, xlim, ylim)
        arr_x.append(px)
        if abs(x) < 1e-5 and not hide_axis:
            pass
            draw.text((px + 3, height - 15), f"{0}", fill=colour_text)
        else:
            if (not hide_grid) or x in xlim:
                draw.line([(px, 0), (px, height)], fill=colour_grid, width=1)
            draw.text((px + 3, height - 15), f"{x:g}", fill=colour_text)

    y_negitive = np.append(np.arange(0, ylim[0] - 1e-9, -steps), ylim[0])
    y_positive = np.append(np.arange(0, ylim[1] + 1e-9, steps), ylim[1])
    # Horizontal lines
    for y in np.concatenate((y_negitive, y_positive)):
        _, py = coord_to_canvas(0, y, width, height, xlim, ylim)
        arr_y.append(py)
        if abs(y) < 1e-5 and not hide_axis:
            pass
            draw.text((3, py + 3), f"{0}", fill=colour_text)
        else:
            if (not hide_grid) or y in ylim:
                draw.line([(0, py), (width, py)], fill=colour_grid, width=1)
            draw.text((3, py + 3), f"{y:g}", fill=colour_text)
    arr_x.sort()
    arr_y.sort()
    return arr_x, arr_y


def draw_canvas(shape_coords, xlim, ylim, grid_steps, hide_grid, hide_axis):

    current_theme = st.context.theme.type
    if current_theme == "light":
        pass
        colour_background = "white"
        colour_point_old = "darkred"
        colour_point_cur = "red"
        colour_text_old = "dimgrey"
        colour_text_cur = "black"
        colour_line_old = "blue"
        colour_line_cur = "green"
        colour_last_line_old = "blue"
        colour_last_line_cur = "orange"
    else:
        colour_background = (14, 17, 23)
        colour_point_old = "darkred"
        colour_point_cur = "red"
        colour_text_old = "lightgray"
        colour_text_cur = "white"
        colour_line_old = "blue"
        colour_line_cur = "green"
        colour_last_line_old = "blue"
        colour_last_line_cur = "orange"
        pass
    # st.html("<script>console.log('Test1: ')<\script>", unsafe_allow_javascript=True)
    # TO-DO: modify to work with multiple shapes
    # TO-DO: add a snap to grid feature:

    # TO?DO: add overlap detection:
    #       Only overlaps if the green line is overlapping
    img = Image.new("RGB", (WIDTH, HEIGHT), colour_background)
    draw = ImageDraw.Draw(img)
    grid_x_lines, grid_y_lines = draw_default_image(
        draw, WIDTH, HEIGHT, xlim, ylim, grid_steps, hide_grid, hide_axis
    )
    last_index = len(shape_coords) - 1
    for point_coords_index in range(len(shape_coords)):
        points = [
            coord_to_canvas(x, y, WIDTH, HEIGHT, xlim, ylim)
            for x, y in shape_coords[point_coords_index]
        ]

        if point_coords_index == last_index:
            col_point = colour_point_cur
            col_text = colour_text_cur
            col_line = colour_line_cur
            col_last_line = colour_last_line_cur

        else:
            col_point = colour_point_old
            col_text = colour_text_old
            col_line = colour_line_old
            col_last_line = colour_last_line_old

        if len(points) >= 2:
            draw.line(points, fill=col_line, width=2)
        if len(points) >= 3:
            draw.line([points[-1], points[0]], fill=col_last_line, width=2)
        r = 5
        for i, (x, y) in enumerate(points):
            draw.text((x + 8, y - 8), str(i + 1), fill=col_text)
            draw.ellipse((x - r, y - r, x + r, y + r), fill=col_point)

    return img, grid_x_lines, grid_y_lines


def display_canvas():
    # TO-DO: turn this from something that can make only one square to many

    if "points" not in st.session_state:
        st.session_state["points"] = [[[0, 0]]]

    cur_shape_index = len(st.session_state["points"]) - 1

    if "last_click_time" not in st.session_state:
        st.session_state["last_click_time"] = None

    canvas_display, canvas_config = st.columns([500, 1000])
    with canvas_config:
        config_tab_names = ["Change domain", "Modify grid"]
        domain_tab, grid_tab = st.tabs(config_tab_names)
        with grid_tab:
            hide_toggles, steps_input, _ = st.columns([120, 200, 600])
            with hide_toggles:
                hide_grid = st.toggle("Hide grid")
                hide_axis = st.toggle("Hide axis")
            with steps_input:
                grid_steps = grid_step_arrow_input(
                    "Grid step", "grid_step_input_value", 0.5
                )
                # grid_steps = st.number_input(
                #     "grid step",
                #     min_value=1e-10,
                #     value=0.5,
                #     step=1.0,
                # )

            bounds_control_area, _ = st.columns([100, 100])
            with bounds_control_area:

                key_prefix = "plane"
                step = grid_steps
                if f"{key_prefix}_x_min_persistant" not in st.session_state:
                    st.session_state[f"{key_prefix}_x_min_persistant"] = -2.5
                if f"{key_prefix}_x_max_persistant" not in st.session_state:
                    st.session_state[f"{key_prefix}_x_max_persistant"] = 2.5
                if f"{key_prefix}_y_min_persistant" not in st.session_state:
                    st.session_state[f"{key_prefix}_y_min_persistant"] = -2.5
                if f"{key_prefix}_y_max_persistant" not in st.session_state:
                    st.session_state[f"{key_prefix}_y_max_persistant"] = 2.5
                if changeVal:
                    arr_shapes = ast.literal_eval(
                        "[" + st.session_state["poly_input_3d_persistent"] + "]"
                    )
                    old_x_min = arr_shapes[0][0][0]
                    old_x_max = arr_shapes[0][0][0]
                    old_y_min = arr_shapes[0][0][1]
                    old_y_max = arr_shapes[0][0][1]
                    for shape in arr_shapes:
                        for point in shape:
                            if old_x_min >= point[0] - grid_steps * 2:
                                old_x_min = point[0] - grid_steps * 2
                            if old_x_max <= point[0] + grid_steps * 2:
                                old_x_max = point[0] + grid_steps * 2
                            if old_y_min >= point[1] - grid_steps * 2:
                                old_y_min = point[1] - grid_steps * 2
                            if old_y_max <= point[1] + grid_steps * 2:
                                old_y_max = point[1] + grid_steps * 2

                    st.session_state.pop(f"{key_prefix}_x_min", None)
                    st.session_state.pop(f"{key_prefix}_y_min", None)
                    st.session_state.pop(f"{key_prefix}_x_max", None)
                    st.session_state.pop(f"{key_prefix}_y_max", None)

                    st.session_state[f"{key_prefix}_x_min_persistant"] = (
                        old_x_min - np.mod(old_x_min, step) - step
                    )
                    st.session_state[f"{key_prefix}_x_max_persistant"] = (
                        old_x_max - np.mod(old_x_max, step) + step
                    )
                    st.session_state[f"{key_prefix}_y_min_persistant"] = (
                        old_y_min - np.mod(old_y_min, step) - step
                    )
                    st.session_state[f"{key_prefix}_y_max_persistant"] = (
                        old_y_max - np.mod(old_y_max, step) + step
                    )

                bounds = plane_bounds_controller(
                    key_prefix="plane",
                    step=step,
                )

                x_min_value = bounds["x_min"]
                x_max_value = bounds["x_max"]
                y_min_value = bounds["y_min"]
                y_max_value = bounds["y_max"]
        with domain_tab:
            # TODO: Add redo button
            snap_to_grid = st.toggle(
                "Enable Snap-To-Grid", key="snap_to_grid", value=True
            )

            if st.button("Toggle shape"):
                if len(st.session_state["points"][cur_shape_index]) <= 2:
                    st.warning("⚠️ Warning: Shape must have more that 2 points")
                elif len(st.session_state["points"]) > 1:
                    old_shape = st.session_state["points"].pop(0)
                    st.session_state["points"].append(old_shape)
                    st.rerun()
                else:
                    st.warning("⚠️ Warning: No shapes left")
            if st.button("New shape"):
                pass
                if len(st.session_state["points"][cur_shape_index]) > 2:
                    st.session_state["points"].append([])
                else:
                    st.warning("⚠️ Warning: Shape must have more that 2 points")
            if st.button("Remove shape"):
                pass
                if len(st.session_state["points"]) == 1:
                    st.session_state["points"] = [[]]
                    st.rerun()
                elif len(st.session_state["points"]) > 1:
                    st.session_state["points"].pop()
                    st.rerun()
                else:
                    st.warning("⚠️ Warning: No shapes left")
            if st.button("Remove last point"):
                if len(st.session_state["points"][cur_shape_index]) > 0:
                    st.session_state["points"][cur_shape_index].pop()
                    st.rerun()
                else:
                    st.warning("⚠️ Warning: Cannot remove point: No points left")
            if st.button("Toggle point"):
                if len(st.session_state["points"][cur_shape_index]) <= 2:
                    st.warning("⚠️ Warning: Shape must have more that 2 points")
                else:
                    old_point = st.session_state["points"][cur_shape_index].pop(0)
                    st.session_state["points"][cur_shape_index].append(old_point)
                    st.rerun()
            if st.button("Clear"):
                st.session_state["points"] = [[]]
                # st.session_state.last_click_time = None
                st.rerun()

    with canvas_display:
        canvas, grid_x_lines, grid_y_lines = draw_canvas(
            st.session_state["points"],
            xlim=(x_min_value, x_max_value),
            ylim=(y_min_value, y_max_value),
            grid_steps=grid_steps,
            hide_grid=hide_grid,
            hide_axis=hide_axis,
        )
        value = streamlit_image_coordinates(
            canvas,
            key="image_click",
            use_column_width="always",
        )

    if value is not None and value["unix_time"] is not None:
        if value["unix_time"] != st.session_state.last_click_time:
            st.session_state.last_click_time = value["unix_time"]
            if snap_to_grid:
                grid_x_lines = [x / WIDTH * value["width"] for x in grid_x_lines]
                grid_y_lines = [y / HEIGHT * value["height"] for y in grid_y_lines]
                x_coord = grid_x_lines[0]
                for x in grid_x_lines:
                    if abs(value["x"] - x) < abs(value["x"] - x_coord):
                        x_coord = x
                y_coord = grid_y_lines[0]
                for y in grid_y_lines:
                    if abs(value["y"] - y) < abs(value["y"] - y_coord):
                        y_coord = y
                # y_coord = grid_y_lines[np.abs(np.array(grid_y_lines) - value["y"]).argmin()]
                pass

                x_coord, y_coord = canvas_to_coord(
                    x_coord,
                    y_coord,
                    value["width"],
                    value["height"],
                    (x_min_value, x_max_value),
                    (y_min_value, y_max_value),
                )
                draw = ImageDraw.Draw(canvas)
                draw.ellipse((x_coord, y_coord, 10, 10), fill="pink")
                # draw.text((x_coord, y_coord), "T", fill="Pink")
            else:
                x_coord, y_coord = canvas_to_coord(
                    value["x"],
                    value["y"],
                    value["width"],
                    value["height"],
                    (x_min_value, x_max_value),
                    (y_min_value, y_max_value),
                )

            st.session_state["points"][cur_shape_index].append(
                (round(x_coord, 2), round(y_coord, 2))
            )
            st.rerun()

    # points_str = "[\n\t" + "\n],[\n\t".join([",\n\t".join(["["+str(x)+","+str(y)+"]" for (x,y) in arr_shape]) for arr_shape in st.session_state["points"]]) + "\n]"

    return points_to_string(st.session_state["points"])


# ~~~~~~~~~~~~~~~~~~~~~~~ Grid arrow keys:
def init_number_state(key, default):
    # st.session_state[key] = str(default)
    if key not in st.session_state:
        st.session_state[key] = str(default)


def adjust_number(key, delta):
    try:
        value = float(st.session_state[key])
    except ValueError:
        value = 0.0

    value += delta
    st.session_state[key] = f"{value:g}"


def read_number(key, fallback=0.0):
    try:
        return float(st.session_state[key])
    except ValueError:
        # st.error(f"Invalid number: {st.session_state[key]}")
        return fallback


def vertical_arrow_input(label, key, default, step=1.0, limit=[-np.inf, np.inf]):
    init_number_state(key, default)

    st.markdown(
        f"<div style='text-align:center; font-size: 0.85rem;'>{label}</div>",
        unsafe_allow_html=True,
    )

    _, button_col, _ = st.columns([1, 1, 1])

    if not is_float(st.session_state[key]):
        st.session_state[key] = str(default)
        st.warning("⚠️ Warning: Unrecodnized float or Integer")

    with button_col:
        st.button(
            "▲",
            key=f"{key}_up",
            use_container_width=True,
            on_click=adjust_number,
            args=(key, step),
            disabled=not read_number(key, default) < limit[1] - step,
        )

    st.text_input(
        label,
        key=key,
        label_visibility="collapsed",
    )

    _, button_col, _ = st.columns([1, 1, 1])
    with button_col:
        st.button(
            "▼",
            key=f"{key}_down",
            use_container_width=True,
            on_click=adjust_number,
            args=(key, -step),
            disabled=not limit[0] + step < read_number(key, default),
        )

    st.session_state[key + "_persistant"] = str(
        min(max(read_number(key, default), limit[0]), limit[1])
    )
    return min(max(read_number(key, default), limit[0]), limit[1])


def horizontal_arrow_input(label, key, default, step=1.0, limit=[-np.inf, np.inf]):
    init_number_state(key, default)

    st.markdown(
        f"<div style='text-align:center; font-size: 0.85rem;'>{label}</div>",
        unsafe_allow_html=True,
    )

    left_btn, value_col, right_btn = st.columns([1, 3, 1])

    if not is_float(st.session_state[key]):
        st.session_state[key] = str(default)
        st.warning("⚠️ Warning: Unrecodnized float or Integer")

    with left_btn:
        st.button(
            "◀",
            key=f"{key}_left",
            use_container_width=True,
            on_click=adjust_number,
            args=(key, -step),
            disabled=not limit[0] + step < read_number(key, default),
        )

    with value_col:
        st.text_input(
            label,
            key=key,
            label_visibility="collapsed",
        )

    with right_btn:
        st.button(
            "▶",
            key=f"{key}_right",
            use_container_width=True,
            on_click=adjust_number,
            args=(key, step),
            disabled=not read_number(key, default) < limit[1] - step,
        )

    st.session_state[key + "_persistant"] = str(read_number(key, default))
    return min(max(read_number(key, default), limit[0]), limit[1])


def grid_step_arrow_input(label, key, default):
    init_number_state(key, default)

    st.markdown(
        f"<div style='text-align:center; font-size: 0.85rem;'>{label}</div>",
        unsafe_allow_html=True,
    )

    value_col, left_btn, right_btn = st.columns([3, 1, 1])

    if not is_float(st.session_state[key]):
        st.session_state[key] = str(default)
        st.warning("⚠️ Warning: Unrecodnized float or Integer")
    elif read_number(key, default) <= 0:
        st.session_state[key] = str(default)
        st.warning("⚠️ Warning: Equal to or less that Zero")

    with value_col:
        st.text_input(
            label,
            key=key,
            label_visibility="collapsed",
        )

    with left_btn:
        st.button(
            "◀",
            key=f"{key}_left",
            use_container_width=True,
            on_click=adjust_number,
            args=(key, -float(st.session_state[key]) / 2),
        )

    with right_btn:
        st.button(
            "▶",
            key=f"{key}_right",
            use_container_width=True,
            on_click=adjust_number,
            args=(key, float(st.session_state[key])),
        )

    st.session_state[key + "_persistant"] = str(abs(read_number(key, default)))
    return read_number(key, default)


def plane_bounds_controller(
    key_prefix="plane",
    step=0.5,
):
    default_x_min = st.session_state[f"{key_prefix}_x_min_persistant"]
    default_x_max = st.session_state[f"{key_prefix}_x_max_persistant"]
    default_y_min = st.session_state[f"{key_prefix}_y_min_persistant"]
    default_y_max = st.session_state[f"{key_prefix}_y_max_persistant"]

    _, top_col, _ = st.columns([1.5, 1, 1.5])

    left_col, centre_col, right_col = st.columns(
        [1.4, 1.2, 1.4],
        vertical_alignment="center",
    )

    _, bottom_col, _ = st.columns([1.5, 1, 1.5])

    with centre_col:
        _, button_space, _ = st.columns([1, 4, 1])
        with button_space:
            st.markdown(
                """
                <div style="
                    border-radius: 8px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin-top: 24px;
                    opacity: 0.75;
                ">
                """,
                unsafe_allow_html=True,
            )
            if st.button(
                "Reset", key=f"{key_prefix}_centre_button", use_container_width=True
            ):
                st.session_state[f"{key_prefix}_x_min_persistant"] = -2.5
                st.session_state[f"{key_prefix}_x_max_persistant"] = 2.5
                st.session_state[f"{key_prefix}_y_min_persistant"] = -2.5
                st.session_state[f"{key_prefix}_y_max_persistant"] = 2.5
                st.rerun()

            st.markdown(
                """
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Top edge
    with top_col:
        y_max_value = vertical_arrow_input(
            "Top edge y",
            key=f"{key_prefix}_y_max",
            default=default_y_max,
            step=step,
            limit=[
                float(st.session_state[f"{key_prefix}_y_min_persistant"]) + 1e-10,
                np.inf,
            ],
        )

    # Middle row: left edge, plane preview, right edge
    with left_col:
        x_min_value = horizontal_arrow_input(
            "Left edge x",
            key=f"{key_prefix}_x_min",
            default=default_x_min,
            step=step,
            limit=[
                -np.inf,
                float(st.session_state[f"{key_prefix}_x_max_persistant"]) - 1e-10,
            ],
        )
    with right_col:
        x_max_value = horizontal_arrow_input(
            "Right edge x",
            key=f"{key_prefix}_x_max",
            default=default_x_max,
            step=step,
            limit=[
                float(st.session_state[f"{key_prefix}_x_min_persistant"]) + 1e-10,
                np.inf,
            ],
        )

    # Bottom edge
    with bottom_col:
        y_min_value = vertical_arrow_input(
            "Bottom edge y",
            key=f"{key_prefix}_y_min",
            default=default_y_min,
            step=step,
            limit=[
                -np.inf,
                float(st.session_state[f"{key_prefix}_y_max_persistant"]) - 1e-10,
            ],
        )

    if x_min_value >= x_max_value:
        st.error("Left edge x must be smaller than right edge x.")

    if y_min_value >= y_max_value:
        st.error("Bottom edge y must be smaller than top edge y.")

    st.session_state[f"{key_prefix}_x_min_persistant"] = x_min_value
    st.session_state[f"{key_prefix}_x_max_persistant"] = x_max_value
    st.session_state[f"{key_prefix}_y_min_persistant"] = y_min_value
    st.session_state[f"{key_prefix}_y_max_persistant"] = y_max_value

    return {
        "x_min": x_min_value,
        "x_max": x_max_value,
        "y_min": y_min_value,
        "y_max": y_max_value,
    }


# ~~~~~~~~~~~~~~~~~~~~~~~
def triangulate_grid_surf(rows, cols):
    bot_l_y, bot_l_x = np.mgrid[0 : rows - 1, 0 : cols - 1]
    top_r_y, top_r_x = np.mgrid[1:rows, 1:cols]
    top_l_y, top_l_x = np.mgrid[1:rows, 0 : cols - 1]
    bot_r_y, bot_r_x = np.mgrid[0 : rows - 1, 1:cols]

    bot_l_y = bot_l_y.flatten()
    bot_l_x = bot_l_x.flatten()
    top_r_y = top_r_y.flatten()
    top_r_x = top_r_x.flatten()
    top_l_y = top_l_y.flatten()
    top_l_x = top_l_x.flatten()
    bot_r_y = bot_r_y.flatten()
    bot_r_x = bot_r_x.flatten()

    i_set = np.concatenate((bot_l_y * cols + bot_l_x, bot_l_y * cols + bot_l_x))
    j_set = np.concatenate((top_r_y * cols + top_r_x, top_l_y * cols + top_l_x))
    k_set = np.concatenate((bot_r_y * cols + bot_r_x, top_r_y * cols + top_r_x))

    return (i_set, j_set, k_set)


def dictionary_inherit(child, parent):
    for key in parent:
        if key in child:
            if isinstance(child[key], dict) and isinstance(parent[key], dict):
                dictionary_inherit(child[key], parent[key])
        else:
            child[key] = parent[key]

    return child


F_COLOR = "#eb5e28"
BASE_COLOR_OLD = "#252422"
BASE_COLOR = "#4287f5"
SIDES_COLOR = "#403d39"
LINE_COLOR = "#000000"

current_theme = st.context.theme.type
if current_theme == "light":
    F_COLOR = "#eb5e28"
    SIDES_COLOR = "#403d39"
else:
    F_COLOR = "#ca3d07"
    # F_COLOR = '#fc6f39'
    SIDES_COLOR = "#eeeeee"

PTLY_MESH_DEF = dict(
    opacity=1.0,
    color="#FFFFFF",
    hoverinfo="x+y+z",
)


PTLY_MESH_DEF = dict(
    opacity=0.49,
    color="#FFFFFF",
    hoverinfo="x+y+z",
    showlegend=False,
)

PTLY_MINOR_LINE_DEF = dict(
    opacity=1,
    mode="lines",
    line=dict(color="#000000", width=1.5),
    hoverinfo="x+y+z",
    showlegend=False,
)

PTLY_MAJOR_LINE_DEF = dict(
    opacity=1,
    mode="lines",
    line=dict(color="#000000", width=5.0),
    hoverinfo="x+y+z",
    showlegend=False,
)

PTLY_2D_LINE_DEF = dict(
    opacity=1,
    mode="lines",
    line=dict(color="#000000", width=2.5),
    hoverinfo="x+y+z",
    showlegend=False,
)

PTLY_F_MESH_DEF = dict(
    color=F_COLOR,
)
dictionary_inherit(PTLY_F_MESH_DEF, PTLY_MESH_DEF)


PTLY_F_MINOR_LINE_DEF = dict(
    line=dict(color=LINE_COLOR),
)
dictionary_inherit(PTLY_F_MINOR_LINE_DEF, PTLY_MINOR_LINE_DEF)


PTLY_F_MAJOR_LINE_DEF = dict(
    line=dict(color=LINE_COLOR),
)
dictionary_inherit(PTLY_F_MAJOR_LINE_DEF, PTLY_MAJOR_LINE_DEF)


PTLY_BASE_MESH_DEF = dict(
    color=BASE_COLOR,
)
dictionary_inherit(PTLY_BASE_MESH_DEF, PTLY_MESH_DEF)


PTLY_BASE_MINOR_LINE_DEF = dict(
    line=dict(color=LINE_COLOR),
)
dictionary_inherit(PTLY_BASE_MINOR_LINE_DEF, PTLY_MINOR_LINE_DEF)


PTLY_BASE_MAJOR_LINE_DEF = dict(
    line=dict(color=LINE_COLOR),
)
dictionary_inherit(PTLY_BASE_MAJOR_LINE_DEF, PTLY_MAJOR_LINE_DEF)


PTLY_SIDES_MESH_DEF = dict(
    color=SIDES_COLOR,
)
dictionary_inherit(PTLY_SIDES_MESH_DEF, PTLY_MESH_DEF)


PTLY_SIDES_MINOR_LINE_DEF = dict(
    line=dict(color=LINE_COLOR),
)
dictionary_inherit(PTLY_SIDES_MINOR_LINE_DEF, PTLY_MINOR_LINE_DEF)


PTLY_SIDES_MAJOR_LINE_DEF = dict(
    line=dict(color=LINE_COLOR),
)
dictionary_inherit(PTLY_SIDES_MAJOR_LINE_DEF, PTLY_MAJOR_LINE_DEF)

PTLY_2D_S_LINE_DEF = dict(
    line=dict(color=F_COLOR),
)
dictionary_inherit(PTLY_2D_S_LINE_DEF, PTLY_2D_LINE_DEF)

PTLY_2D_R_LINE_DEF = dict(
    line=dict(color=BASE_COLOR),
)
dictionary_inherit(PTLY_2D_R_LINE_DEF, PTLY_2D_LINE_DEF)

PTLY_2D_TRIANGLE_LINE_DEF = dict(
    line=dict(color=LINE_COLOR, width=1.5), legendgroup="2DTriagLines"
)
dictionary_inherit(PTLY_2D_TRIANGLE_LINE_DEF, PTLY_2D_LINE_DEF)

st.set_page_config(layout="wide")

input_tab, config_tab = st.tabs(
    ["Parameters", "Config"], key="input_config_tabs", on_change="rerun"
)

if "cfg3d_rad_res" not in st.session_state:
    st.session_state["cfg3d_rad_res"] = 50
if "cfg3d_xy_res" not in st.session_state:
    st.session_state["cfg3d_xy_res"] = 50
if "cfg3d_z_res" not in st.session_state:
    st.session_state["cfg3d_z_res"] = 50
if "cfg3d_integ_iters" not in st.session_state:
    st.session_state["cfg3d_integ_iters"] = 100
if "cfg3d_tol" not in st.session_state:
    st.session_state["cfg3d_tol"] = -9

if config_tab.open:
    with config_tab:
        st.write("# Config")
        rad_res3d = st.number_input(
            "Triangle Radial Resolution",
            help="Sets the radial resolution for the top bottom meshes of each produced triangle.",
            key="cfg3d_rad_res",
            min_value=50,
            max_value=200,
            value=50,
        )

        xy_res3d = st.number_input(
            "Triangle XY Resolution",
            help="Sets the xy resolution for the sides of each produced triangle.",
            key="cfg3d_xy_res",
            min_value=50,
            max_value=200,
            value=50,
        )

        z_res3d = st.number_input(
            "Triangle Z Resolution",
            help="Sets the z resolution for the sides of each produced triangle.",
            key="cfg3d_z_res",
            min_value=50,
            max_value=200,
            value=50,
        )

        integ_iters = st.number_input(
            "Maximum Integration Iterations",
            help="Sets the maximum adaptive Gauss-Kronrod iterations before failure.",
            key="cfg3d_integ_iters",
            min_value=10,
            max_value=10000,
            value=100,
        )

        tol = 10 ** st.number_input(
            "Integration Tolerance Base 10 Exponent",
            help="Sets the absolute integration tolerance exponent.",
            key="cfg3d_tol",
            min_value=-12,
            max_value=0,
            value=-9,
        )

if input_tab.open:
    with input_tab:
        header_col, preset_col = st.columns([90, 10])
        with preset_col:
            st.write(" ")
            presets = ["Default", "Prismatoid", "Helix", "Pyramid", "Clear"]

            if "selected_preset" not in st.session_state:
                st.session_state["selected_preset"] = ""
            new_preset = st.selectbox("**Choose a Preset**", list(presets), index=0)
            if new_preset != st.session_state["selected_preset"]:
                st.session_state["selected_preset"] = new_preset
                if new_preset == presets[0]:
                    f_latex_input = "x + 2"
                    c1_latex_input = "-z"
                    c2_latex_input = "0"
                    polygons_input = "[\n\t[-1,-1],\n\t[-1,1],\n\t[1,1],\n\t[1,-1]\n],[\n\t[-0.5, -0.5],\n\t[-0.5, 0.5],\n\t[0.5, 0.5],\n\t[0.5, -0.5]\n]"
                elif new_preset == presets[1]:
                    f_latex_input = "-x -y + 8"
                    c1_latex_input = "\\frac{z}{2}"
                    c2_latex_input = "z"
                    polygons_input = (
                        "[\n\t[1.6,3.2],\n\t[0.8,5.6],\n\t[4,4],\n\t[4.8,1.6]\n]"
                    )
                elif new_preset == presets[2]:
                    f_latex_input = "2\\pi + x - y "
                    c1_latex_input = "1- \\cos(z)"
                    c2_latex_input = "\\sin(z)"
                    polygons_input = "[\n\t[1,1],\n\t[1,2],\n\t[2,2],\n\t[2,1]\n]"
                elif new_preset == presets[3]:
                    f_latex_input = r"""1-\left(\left(x\cos\left(2\pi\left(1-\sqrt{x^2+y^2}\right)\right)+y\sin\left(2\pi\left(1-\sqrt{x^2+y^2}\right)\right)\right)^{12}+\left(-y\cos\left(2\pi\left(1-\sqrt{x^2+y^2}\right)\right)+x\sin\left(2\pi\left(1-\sqrt{x^2+y^2}\right)\right)\right)^{12}\right)^{\frac{1}{12}}"""
                    c1_latex_input = "0"
                    c2_latex_input = "0"
                    polygons_input = "[\n\t[-1,-1],\n\t[-1,1],\n\t[1,1],\n\t[1,-1]\n]"
                # elif (new_preset == presets[4]):
                #     f_latex_input = "0"
                #     c1_latex_input = "0"
                #     c2_latex_input = "0"
                #     polygons_input = "[\n\t[0.0,0.0],\n\t[1.0,0.0],\n\t[0.0,1.0],\n\t[1.0,1.0],\n\t[0.0,2.0]\n]"
                # elif (new_preset == presets[5]):
                #     f_latex_input = "0"
                #     c1_latex_input = "0"
                #     c2_latex_input = "0"
                #     polygons_input = "[\n\t[0.0,0.0],\n\t[0.5,0.0],\n\t[-0.5,-0.5],\n\t[0.0,0.5]\n]"
                # elif new_preset == presets[6]:
                #     f_latex_input = "2"
                #     c1_latex_input = "3"
                #     c2_latex_input = "1"
                #     polygons_input = "[\n\t[-1,-1],\n\t[-1,1],\n\t[1,1],\n\t[1,-1]\n]"
                else:
                    f_latex_input = "0"
                    c1_latex_input = "0"
                    c2_latex_input = "0"
                    polygons_input = "[\n\t[0.0,0.0]\n]"
                #  Change preset to new preset and rerun

                st.session_state["f_latex_input_value"] = f_latex_input
                st.session_state["c1_latex_input_value"] = c1_latex_input
                st.session_state["c2_latex_input_value"] = c2_latex_input
                st.session_state["poly_input_3d_persistent"] = polygons_input
                st.session_state["poly_input_3d"] = None
                st.session_state["points"] = None
                changeVal = True
            else:
                changeVal = False

        with header_col:
            st.write("# Parameters")
        (
            f_label_col,
            f_input_col,
            c1_label_col,
            c1_input_col,
            c2_label_col,
            c2_input_col,
        ) = st.columns([0.7, 3, 0.7, 3, 0.7, 3])

        with f_label_col:
            st.write("###")
            st.latex("f(x, y)=")

        with f_input_col:
            f_latex_input = math_input_component(
                key="f_latex_input",
                value=st.session_state["f_latex_input_value"],
                variables="xy",
                changeVal=changeVal,
            )
            # eg variables="xyz"
            show_f_latex_button = st.toggle(
                "Show equation details", key="show_f_latex_button", value=False
            )

            with st.expander("latex", expanded=show_f_latex_button):
                st.code(f_latex_input, language="latex")

        with c1_label_col:
            st.write("###")
            st.latex("c_x(z)=")

        with c1_input_col:
            c1_latex_input = math_input_component(
                key="c1_latex_input",
                value=st.session_state["c1_latex_input_value"],
                variables="z",
                changeVal=changeVal,
            )
            # eg variables="xyz"
            show_c1_latex_button = st.toggle(
                "Show equation details", key="show_c1_latex_button", value=False
            )
            with st.expander("latex", expanded=show_c1_latex_button):
                st.code(c1_latex_input, language="latex")

        with c2_label_col:
            st.write("###")
            st.latex("c_y(z)=")

        with c2_input_col:
            c2_latex_input = math_input_component(
                key="c2_latex_input",
                value=st.session_state["c2_latex_input_value"],
                variables="z",
                changeVal=changeVal,
            )
            # eg variables="xyz"
            show_c2_latex_button = st.toggle(
                "Show equation details", key="show_c2_latex_button", value=False
            )

            with st.expander("latex", expanded=show_c2_latex_button):
                st.code(c2_latex_input, language="latex")

        st.subheader("Domain selection type:")
        options = ["Text box", "2D-Plane"]
        selection = st.segmented_control(
            "Choose one:", options, default=options[0], required=True
        )

        polygons_label_col, polygons_input_col = st.columns([1, 11])

        initial_polygon_set = "[\n\t[-1,-1],\n\t[-1,1],\n\t[1,1],\n\t[1,-1]\n],[\n\t[-0.5, -0.5],\n\t[-0.5, 0.5],\n\t[0.5, 0.5],\n\t[0.5, -0.5]\n]"
        if "poly_input_3d_persistent" not in st.session_state:
            st.session_state["poly_input_3d_persistent"] = initial_polygon_set

        with polygons_label_col:
            st.write("###")
            st.latex("S=")
            if selection == options[0]:
                if st.button("Format Array"):
                    try:
                        points = ast.literal_eval(
                            "[" + st.session_state["poly_input_3d_persistent"] + "]"
                        )
                        st.session_state["poly_input_3d"] = points_to_string(points)
                    except:
                        st.warning("⚠️ Warning: Failed to format")

        with polygons_input_col:
            if selection == options[0]:
                if (
                    "poly_input_3d" not in st.session_state
                    or st.session_state["poly_input_3d"] == None
                ):
                    st.session_state["poly_input_3d"] = st.session_state[
                        "poly_input_3d_persistent"
                    ]

                polygons_input = st.text_area(
                    "*", label_visibility="hidden", key="poly_input_3d", height=300
                )

                st.session_state["poly_input_3d_persistent"] = polygons_input
                st.session_state["points"] = None
            elif selection == options[1]:
                if (
                    "points" not in st.session_state
                    or st.session_state["points"] == None
                ):
                    try:
                        st.session_state["points"] = ast.literal_eval(
                            "[" + st.session_state["poly_input_3d_persistent"] + "]"
                        )

                        # if (st.session_state["points"]==[[]]):
                        #     st.warning("⚠️ Warning: No points. Adding ");
                        #     st.session_state["points"] = [[[0.0,0.0]]];

                    except:
                        st.warning(
                            "⚠️ Warning: Error when converting polygon list. Reverting to default"
                        )
                        st.session_state["points"] = ast.literal_eval(
                            "[" + initial_polygon_set + "]"
                        )
                        st.session_state["poly_input_3d_persistent"] = (
                            initial_polygon_set
                        )

                polygons_input = display_canvas()
                # if (polygons_input == "[\n\t\n]"):
                #     polygons_input = "[\n\t[0,0]\n]"
                if polygons_input.endswith(",[\n\t\n]"):
                    polygons_input = polygons_input[:-6]
                    pass
                st.session_state["poly_input_3d_persistent"] = polygons_input
                st.session_state["poly_input_3d"] = None

                if "show_canvas_points_persistent" not in st.session_state:
                    st.session_state["show_canvas_points_persistent"] = False
                show_canvas_points = st.session_state["show_canvas_points_persistent"]
                show_canvas_points = st.toggle(
                    "Show exact values",
                    key="show_canvas_points",
                    value=show_canvas_points,
                )
                st.session_state["show_canvas_points_persistent"] = show_canvas_points
                with st.expander("", expanded=show_canvas_points):
                    st.code(polygons_input, language="latex")

            else:
                polygons_input = st.session_state["poly_input_3d_persistent"]

        gen_button_and_toggle, _ = st.columns([10, 7])

        f_expr = str(f_latex_input)
        c1_expr = str(c1_latex_input)
        c2_expr = str(c2_latex_input)
        poly_set_expr = str(polygons_input)
        with gen_button_and_toggle:
            gen_button_col, gen_toggle_col, gen_3D_print_export, gen_3D_spinner = (
                st.columns([10, 10, 10, 30])
            )
            if "gen_toggle_3d_persistent" not in st.session_state:
                st.session_state["gen_toggle_3d_persistent"] = False
            with gen_toggle_col:
                if "gen_toggle_3d" in st.session_state:
                    gen_toggle = st.toggle("Auto Generate", key="gen_toggle_3d")
                else:
                    gen_toggle = st.toggle(
                        "Auto Generate",
                        key="gen_toggle_3d",
                        value=st.session_state["gen_toggle_3d_persistent"],
                    )

            with gen_button_col:
                gen_button = st.button(
                    "Generate", key="gen_button_3d", disabled=gen_toggle
                )

            gen_toggle = gen_toggle or gen_button
            st.session_state["gen_toggle_3d_persistent"] = gen_toggle
            with gen_3D_print_export:
                pass
                if st.button(label="Download STL File"):
                    with gen_3D_spinner:
                        try:
                            with st.spinner("Generating STL..."):
                                rad_res3d = st.session_state["cfg3d_rad_res"]
                                xy_res3d = st.session_state["cfg3d_xy_res"]
                                z_res3d = st.session_state["cfg3d_z_res"]
                                integ_iters = st.session_state["cfg3d_integ_iters"]
                                tol = 10 ** st.session_state["cfg3d_tol"]

                                displays = display_cav3d(
                                    f_expr,
                                    c1_expr,
                                    c2_expr,
                                    poly_set_expr,
                                    True,
                                    rad_res3d,
                                    xy_res3d,
                                    z_res3d,
                                    integ_iters,
                                    tol,
                                )
                                # browser_script = _browser_download_script(
                                #         b"hello from streamlit",
                                #         "test.txt",
                                #         "text/plain",
                                #     )
                                browser_script = export_cav3d_displays_to_stl(
                                    displays,
                                    "cavalieri_model.stl",
                                    xy_scale=10.0,
                                    z_scale=10.0,
                                    base_z=0.0,
                                )
                                st.html(browser_script, unsafe_allow_javascript=True)

                        except Exception as ex:
                            st.warning(f"⚠️ Download failed: {ex}")

        # if (changeVal):
        #     st.rerun();

    if gen_toggle and not changeVal:
        st.divider()
        fig_3d_integral = make_subplots(
            1,
            1,
            specs=[[{"type": "mesh3d"}]],
            subplot_titles=["3D Cavalieri Integral"],
        )
        fig_3d_integral["layout"]["height"] = 800
        fig_3d_integral.update_annotations(font_size=24)
        fig_3d_integral.update_layout(
            scene=dict(
                camera=dict(
                    # Flipped the default 1.25 to -1.25 to rotate the camera to the opposite side
                    eye=dict(x=-1.25, y=-1.25, z=1.25)
                )
            )
        )
        fig_2d_regions = make_subplots(
            1,
            2,
            shared_xaxes=True,
            shared_yaxes=True,
            specs=[[{"type": "scatter"}, {"type": "scatter"}]],
            subplot_titles=["S Region", "R Region"],
        )
        fig_2d_regions.update_annotations(font_size=24)
        displays = None
        try:
            rad_res3d = st.session_state["cfg3d_rad_res"]
            xy_res3d = st.session_state["cfg3d_xy_res"]
            z_res3d = st.session_state["cfg3d_z_res"]
            integ_iters = st.session_state["cfg3d_integ_iters"]
            tol = 10 ** st.session_state["cfg3d_tol"]
            displays = display_cav3d(
                f_expr,
                c1_expr,
                c2_expr,
                poly_set_expr,
                True,
                rad_res3d,
                xy_res3d,
                z_res3d,
                integ_iters,
                tol,
            )
        except Exception as ex:
            st.warning(f"⚠️ Warning: An error has occurred: {ex}")

        if displays is not None:
            make_triangle_legend = True
            curtain_id_map = dict()
            triag_integ_df = []
            accu_sum = 0
            accu_err = 0
            for display in displays:
                iv, ierr = display.integ_value
                accu_sum += iv
                accu_err += ierr
                triag = np.array(display.triag)

                triag_integ_df.append(
                    [
                        f"({triag[0, 0]:.2e}, {triag[0, 1]:.2e})--({triag[1, 0]:.2e}, {triag[1, 1]:.2e})--({triag[2, 0]:.2e}, {triag[2, 1]:.2e})",
                        iv,
                        ierr,
                    ]
                )
                top_mesh = np.array(display.top_mesh)
                bot_mesh = np.array(display.bot_mesh)
                i, j, k = triangulate_grid_surf(bot_mesh.shape[0], bot_mesh.shape[1])
                # Top mesh
                fig_3d_integral.add_trace(
                    go.Mesh3d(
                        x=top_mesh[..., 0].flatten(),
                        y=top_mesh[..., 1].flatten(),
                        z=top_mesh[..., 2].flatten(),
                        i=i,
                        j=j,
                        k=k,
                        **PTLY_F_MESH_DEF,
                    ),
                    row=1,
                    col=1,
                )

                # Top mesh tracing
                fig_3d_integral.add_trace(
                    go.Scatter3d(
                        x=top_mesh[-1, :, 0],
                        y=top_mesh[-1, :, 1],
                        z=top_mesh[-1, :, 2],
                        **PTLY_F_MINOR_LINE_DEF,
                    ),
                    row=1,
                    col=1,
                )

                xv = bot_mesh[..., 0].flatten()
                # Bottom mesh
                fig_3d_integral.add_trace(
                    go.Mesh3d(
                        x=xv,
                        y=bot_mesh[..., 1].flatten(),
                        z=np.zeros_like(xv),
                        i=i,
                        j=j,
                        k=k,
                        **PTLY_BASE_MESH_DEF,
                    ),
                    row=1,
                    col=1,
                )

                # Bottom mesh tracing
                fig_3d_integral.add_trace(
                    go.Scatter3d(
                        x=bot_mesh[-1, :, 0],
                        y=bot_mesh[-1, :, 1],
                        z=np.zeros_like(bot_mesh[-1, :, 0]),
                        **PTLY_BASE_MINOR_LINE_DEF,
                    ),
                    row=1,
                    col=1,
                )

                curtains = np.array(display.curtains)
                for curtain in curtains:
                    a = curtain[-1, 0, :]
                    b = curtain[-1, -1, :]

                    if a[0] < b[0]:
                        curtain_id = str([a, b])
                    elif a[0] > b[0]:
                        curtain_id = str([b, a])
                    elif a[1] < b[1]:
                        curtain_id = str([a, b])
                    else:
                        curtain_id = str([b, a])
                    if curtain_id in curtain_id_map:
                        curtain_id_map[curtain_id][0] += 1
                    else:
                        curtain_id_map[curtain_id] = [0, curtain]

            triag_integ_df.append(["Total", accu_sum, accu_err])
            triag_integ_df = pd.DataFrame(
                triag_integ_df,
                columns=["Triangle", "Integration Value", "Estimated Error"],
                index=None,
            )
            for repititions, curtain in curtain_id_map.values():
                i, j, k = triangulate_grid_surf(curtain.shape[0], curtain.shape[1])
                if repititions == 0:
                    # Curtain mesh
                    fig_3d_integral.add_trace(
                        go.Mesh3d(
                            x=curtain[..., 0].flatten(),
                            y=curtain[..., 1].flatten(),
                            z=curtain[..., 2].flatten(),
                            i=i,
                            j=j,
                            k=k,
                            **PTLY_SIDES_MESH_DEF,
                        )
                    )

                    # Curtain left side major line
                    fig_3d_integral.add_trace(
                        go.Scatter3d(
                            x=curtain[:, 0, 0],
                            y=curtain[:, 0, 1],
                            z=curtain[:, 0, 2],
                            **PTLY_SIDES_MAJOR_LINE_DEF,
                        )
                    )

                    # Curtain left side major line
                    fig_3d_integral.add_trace(
                        go.Scatter3d(
                            x=curtain[:, -1, 0],
                            y=curtain[:, -1, 1],
                            z=curtain[:, -1, 2],
                            **PTLY_SIDES_MAJOR_LINE_DEF,
                        )
                    )

                    # Curtain top major line
                    fig_3d_integral.add_trace(
                        go.Scatter3d(
                            x=curtain[-1, :, 0],
                            y=curtain[-1, :, 1],
                            z=curtain[-1, :, 2],
                            **PTLY_F_MAJOR_LINE_DEF,
                        )
                    )

                    # Curtain bottom major line
                    fig_3d_integral.add_trace(
                        go.Scatter3d(
                            x=curtain[0, :, 0],
                            y=curtain[0, :, 1],
                            z=curtain[0, :, 2],
                            **PTLY_F_MAJOR_LINE_DEF,
                        )
                    )

                    # S Edge Line
                    fig_2d_regions.add_trace(
                        go.Scatter(
                            x=curtain[-1, :, 0],
                            y=curtain[-1, :, 1],
                            **PTLY_2D_S_LINE_DEF,
                        ),
                        row=1,
                        col=1,
                    )

                    # R Edge Line
                    fig_2d_regions.add_trace(
                        go.Scatter(
                            x=curtain[0, :, 0], y=curtain[0, :, 1], **PTLY_2D_R_LINE_DEF
                        ),
                        row=1,
                        col=2,
                    )
                else:
                    # S Triangulation Line
                    fig_2d_regions.add_trace(
                        go.Scatter(
                            x=curtain[-1, :, 0],
                            y=curtain[-1, :, 1],
                            name="Triangulation",
                            **PTLY_2D_TRIANGLE_LINE_DEF,
                        ),
                        row=1,
                        col=1,
                    )

                    # R Triangulation Line
                    fig_2d_regions.add_trace(
                        go.Scatter(
                            x=curtain[0, :, 0],
                            y=curtain[0, :, 1],
                            **dictionary_inherit(
                                dict(
                                    name="Triangulation",
                                    showlegend=make_triangle_legend,
                                ),
                                PTLY_2D_TRIANGLE_LINE_DEF,
                            ),
                        ),
                        row=1,
                        col=2,
                    )

                    make_triangle_legend = False

            cav_int_tab, regions_tab, integ_tab = st.tabs(
                ["3D Integral", "R and S", "Triangle Integration Values"]
            )

            with cav_int_tab:
                if not "fig_3d_integral" in locals():
                    fig_3d_integral = st.session_state.get("fig_3d_integral")

                if fig_3d_integral:
                    st.plotly_chart(fig_3d_integral, width="stretch")
                    st.session_state["fig_3d_integral"] = fig_3d_integral

            with regions_tab:
                if not "fig_2d_regions" in locals():
                    fig_2d_regions = st.session_state.get("fig_2d_regions")

                if fig_2d_regions:
                    st.plotly_chart(fig_2d_regions, width="stretch")
                    st.session_state["fig_2d_regions"] = fig_2d_regions

            with integ_tab:
                if not "triag_integ_df" in locals():
                    triag_integ_df = st.session_state.get("triag_integ_df")

                if not triag_integ_df is None:
                    st.dataframe(
                        triag_integ_df.style.format(
                            "{:.4e}", subset=["Integration Value", "Estimated Error"]
                        )
                    )
                    st.session_state["triag_integ_df"] = triag_integ_df
