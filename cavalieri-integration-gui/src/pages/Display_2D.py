import ast
import streamlit as st

# import streamlit.components.v1 as components
from enum import Enum, auto
from typing import cast


from cavint import display_cav2d, display_cav2d_rs, display_cav2d_qs
from utils.math_component import math_input_component

import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd

pd.set_option("display.float_format", "{:.3e}".format)

DEBUG_FLAG = False


def dprint(*args, **kwargs):
    if DEBUG_FLAG:
        print(*args, **kwargs)


displays = None


class DisplayFormat(Enum):
    CAVALIERI_RIEMANN_INT = auto()
    QUADRILATERAL_STRIPS = auto()
    OTHER = auto()


# For demo 2:
# Add a ability to change how many intermediary curves there are
# 3D printing.
# Update 3D GUI

# TO-DO: fix text box not loading
# add toggle for changing textbox to sliders

# TO-DO: Rewrite the slider section.

# TO-DO: Rewrite the rust section to take in Latex instead of his custom format.

# ~~~~~~~~~~~~ Latex input setup ~~~~~~~~~~~~~~~
## l_expr: str The latex expresion recieved in the input box

# TEST: \frac{\left(x^2+7+8-9+\pi+e+\ln(4)+\sqrt5\right)\left(\sin(1)+\cos(2)+\tan(3)+\sinh(0)+\cosh(x)+\tanh(x)\right)}{\operatorname{\mathrm{asin}}\left(\frac12\right)+\operatorname{\mathrm{acos}}\left(\frac12\right)+\operatorname{\mathrm{atan}}\left(x^2\right)+\operatorname{\mathrm{asinh}}(x)+\operatorname{\mathrm{acosh}}(6)+\operatorname{\mathrm{atanh}}\left(\frac15\right)+x^2}

# \frac{\left(\frac{\left(x^2+{x}^2+x^{x+1}+\left(x+1\right)^{x^2}+{\left(x+1\right)}^{\left(x+1\right)^2}+\sqrt{x+1}+\sqrt{x^2+\sqrt{x+1}}+\ln(x+1)+\ln\left(x^2+{x}^2+1\right)+\sin(x)+\cos(x)+\tan\left(\frac{x}{4}\right)+\sinh(x)+\cosh(x)+\tanh(x)\right)^2}{\left(\operatorname{\mathrm{asin}}\left(\frac{x}{2}\right)+\operatorname{\mathrm{acos}}\left(\frac{x}{2}\right)+\operatorname{\mathrm{atan}}\left(x^2\right)+\operatorname{\mathrm{asinh}}(x)+\operatorname{\mathrm{acosh}}(x+1+0.01)+\operatorname{\mathrm{atanh}}\left(\frac{x}{2}\right)+1\right)^2}+\frac{\sqrt{\frac{x^2+\sqrt{x+1}}{\ln(x+1)+1}}+\sqrt{\frac{\sin(x)^2+\cos(x)^2+\tanh(x)^2+1}{x+1}}}{\frac{x+1}{2}+\frac{\sqrt{x+1}}{x+1}}+\left(\frac{\sin(x)}{\cos(x)+2}\right)^2+\left(\frac{\tan\left(\frac{x}{4}\right)}{x+1}\right)^3+\sin\left(x^2\right)+\cos\left({x}^2\right)+\tan\left(\frac{x^3}{4}\right)+\sin(x)^{\cos(x)+1}+\cos(x)^2+\left(\tanh(x)+1\right)^{\sin(x)+1}+\left(\sqrt{x+1}\right)^{\sqrt{x+1}}+\left(\ln(x+1)+1\right)^2+\sqrt{\left(x+\frac12\right)^2+\left(x+\frac13\right)^3}+\frac{\operatorname{\mathrm{asin}}\left(\frac{\sin(x)}{2}\right)+\operatorname{\mathrm{acos}}\left(\frac{\cos(x)}{2}\right)+\operatorname{\mathrm{atan}}\left({x}^3\right)}{\operatorname{\mathrm{asinh}}\left(\frac{x}{2}\right)+\operatorname{\mathrm{acosh}}(x+1+0.01)+\operatorname{\mathrm{atanh}}\left(\frac{\tanh(x)}{2}\right)+1}+\left(\frac{\sqrt{x+1}+\ln(x+1)+1}{x+1}\right)^{\left(\frac{x+1}{2}\right)}+\sqrt{\left(\frac{\sin(x)+\cos(x)+1}{2}\right)^2+\left(\frac{\sinh(x)+\cosh(x)}{2}\right)^2}+\frac{\left(x^2+{x}^2\right)^2+\left(\sqrt{x+1}\right)^2+\left(\frac{x+1}{2}\right)^3}{\left(\ln(x+1)+1\right)^2+\left(\operatorname{\mathrm{atan}}(x)+1\right)^2}\right)}{16}


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
.interval-buttons div[data-testid="stButton"] > button {
    width: 100%;
    height: 42px;
    }
div[data-testid="stAppDeployButton"] {
    display: none !important;
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


# ~~~~~~~~~~~~ Domain selection bars ~~~~~~~~~~~~~~~


def get_slider_domain_name(domain: str):
    return "slider_" + domain


def get_slider_index_name(domain: str, index: int):
    return get_slider_domain_name(domain) + "_" + str(index)


# ~~~~~~~~~~ Getters


def get_slider_domain_value(domain: str):
    return st.session_state[get_slider_domain_name(domain)]


def get_sliders_size(domain: str):
    return len(get_slider_domain_value(domain))


def get_slider_values(domain: str, index: int):
    return get_slider_domain_value(domain)[index]


def get_slider_string(domain: str):
    pass
    output = ""
    # get_slider_domain_value(domain);
    for index in range(get_sliders_size(domain)):
        cur_arr = get_slider_values(domain, index)
        output += "[" + str(cur_arr[0]) + "," + str(cur_arr[1]) + "]"
        output += ","
    return output[:-1]


# ~~~~~~~~~~ Setters
def set_slider_domain_value(domain: str, new_value):
    st.session_state[get_slider_domain_name(domain)] = new_value
    pass


def set_slider_values(domain: str, index: int, new_value):
    st.session_state[get_slider_domain_name(domain)][index] = new_value
    pass


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# ~~~~~~~~~~~~~~~~~~~~ Sections ~~~~~~~~~~~~~~~~~~~~~~~~~~
def x_interval_section(domain: str):
    # TO-DO: REWITE  THIS ENTIRE SECTION

    if (get_slider_domain_name(domain) not in st.session_state) or (
        "x_intervals_input_" + domain not in st.session_state
    ):
        st.session_state[get_slider_domain_name(domain)] = [[0.0, 1.0, -1.0, 2.0]]
    st.session_state["x_intervals_input_" + domain] = get_slider_string(domain)

    st.subheader("Domain selection")

    input_options = ["Text box", "Sliders"]
    selection = st.segmented_control(
        "Choose one:",
        input_options,
        key="segment_" + domain,
        default=input_options[0],
        required=True,
    )

    # "x_intervals_input_"+ domain is true value
    if selection == input_options[0]:
        pass
        x_intervals_label_col, x_intervals_input_col = st.columns([1, 11])
        with x_intervals_label_col:
            # st.write('###')
            st.latex("S=")

        # Updates to text_box
        if "x_interval_text_box_" + domain in st.session_state:
            if (
                str(st.session_state["x_intervals_input_" + domain])
                != st.session_state["x_interval_text_box_" + domain]
            ):

                x_bounds_input = st.session_state["x_interval_text_box_" + domain]
                all_sliders = get_slider_domain_value(domain)
                x_bounds_input = "[" + x_bounds_input + "]"

                try:
                    new_bounds_arr = ast.literal_eval(x_bounds_input)
                    test_arr = np.array(new_bounds_arr)
                except:
                    st.warning(
                        "⚠️ Warning: Failed to convert list. Reverting to default"
                    )
                    new_bounds_arr = None

                if new_bounds_arr != None:
                    if len(new_bounds_arr) < len(all_sliders):
                        while len(new_bounds_arr) < len(all_sliders):
                            all_sliders.pop()
                        st.rerun()
                    changed_slider = False
                    for index in range(len(new_bounds_arr)):
                        new_slider_arr = new_bounds_arr[index]
                        new_slider_arr = compare_subinterval_with_neighbours(
                            new_slider_arr, domain, index
                        )

                        if index >= len(all_sliders):
                            all_sliders.append(
                                [
                                    new_slider_arr[0],
                                    new_slider_arr[1],
                                    np.floor(new_slider_arr[0]) - 1.0,
                                    np.ceil(new_slider_arr[1]) + 1.0,
                                ]
                            )
                        cur_slider_arr = all_sliders[index]

                        if not (
                            cur_slider_arr[0] == new_slider_arr[0]
                            and cur_slider_arr[1] == new_slider_arr[1]
                        ):
                            # TO-DO: Input validation
                            all_sliders[index][0] = new_slider_arr[0]
                            all_sliders[index][1] = new_slider_arr[1]
                            all_sliders[index][2] = min(
                                all_sliders[index][2], np.floor(new_slider_arr[0]) - 1
                            )
                            all_sliders[index][3] = max(
                                all_sliders[index][3], np.ceil(new_slider_arr[1]) + 1
                            )
                            set_slider_domain_value(domain, all_sliders)
                            changed_slider = True
                    if changed_slider:
                        st.rerun()
        with x_intervals_input_col:

            x_interval_box, x_handle_bars = st.columns([7, 3])
            with x_interval_box:
                st.session_state["x_interval_text_box_" + domain] = get_slider_string(
                    domain
                )
                st.text_area(
                    "*",
                    label_visibility="collapsed",
                    key="x_interval_text_box_" + domain,
                )

    if selection == input_options[1]:
        pass
        # ~~~~~~~~~~~~~~~~~~~~~ Input validation and initialization: ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        if get_slider_domain_value(domain) == []:
            set_slider_domain_value(domain, [[0.0, 1.0, -1.0, 2.0]])
            st.warning("⚠️ Warning: Failed to convert list. Reverting to default")

        if "add_interval_slider_" + domain not in st.session_state:
            st.session_state["add_interval_slider_" + domain] = False
        if "rem_interval_slider_" + domain not in st.session_state:
            st.session_state["rem_interval_slider_" + domain] = False

        if st.session_state["add_interval_slider_" + domain]:
            st.session_state["add_interval_slider_" + domain] = False
            all_sliders = get_slider_domain_value(domain)
            last_arr = all_sliders[-1]
            all_sliders.append(
                [last_arr[1] + 1.0, last_arr[1] + 2.0, last_arr[1], last_arr[1] + 3.0]
            )
            # st.session_state["x_interval_text_box_"+domain] += "," + str(all_sliders[-1][:2]).replace(" ", "");

            st.session_state["x_interval_text_box_" + domain] = get_slider_string(
                domain
            )
            st.rerun()
        if st.session_state["rem_interval_slider_" + domain]:
            st.session_state["rem_interval_slider_" + domain] = False
            if get_sliders_size(domain) > 1:
                all_sliders = get_slider_domain_value(domain)
                all_sliders.pop()
                st.session_state["x_interval_text_box_" + domain] = get_slider_string(
                    domain
                )
                st.rerun()
            else:
                st.warning("⚠️ Warning: Must have at least 1 interval")
                # st.text("Must have at least 1 interval");
                # st.markdown(
                #     '<div style="text-align: right;"><b>Must have at least 1 interval</b></div>',
                #     unsafe_allow_html=True
                #     )

        x_intervals_label_col, x_intervals_input_col = st.columns([1, 11])
        with x_intervals_label_col:
            # st.write('###')
            st.latex("S=")
            add_slider_button = st.button(
                "Add slider", key="button_add_slider_" + domain, width="stretch"
            )
            if add_slider_button:
                st.session_state["add_interval_slider_" + domain] = True
                st.rerun()
            rem_slider_button = st.button(
                "Remove slider",
                key="button_rem_slider_" + domain,
                width="stretch",
            )
            if rem_slider_button:
                st.session_state["rem_interval_slider_" + domain] = True
                st.rerun()
        with x_intervals_input_col:
            # Updates to Sliders or number_inputs
            for index in range(get_sliders_size(domain)):
                if (
                    "x_slider_" + domain + "_index_" + str(index)
                    not in st.session_state
                ):
                    continue
                elif (
                    "x_slider_" + domain + "_index_" + str(index)
                    not in st.session_state
                ):
                    continue
                all_sliders = get_slider_domain_value(domain)
                # This needs to get reset every loop
                cur_slider_arr = all_sliders[index]
                start_slider, end_slider = st.session_state[
                    "x_slider_" + domain + "_index_" + str(index)
                ]
                start_input = st.session_state[
                    "x_interval_STR_number_input_" + domain + "_index_" + str(index)
                ]
                end_input = st.session_state[
                    "x_interval_END_number_input_" + domain + "_index_" + str(index)
                ]
                minim = st.session_state[
                    "x_interval_MIN_number_input_" + domain + "_index_" + str(index)
                ]
                maxim = st.session_state[
                    "x_interval_MAX_number_input_" + domain + "_index_" + str(index)
                ]

                if start_slider != cur_slider_arr[0] or end_slider != cur_slider_arr[1]:
                    start_slider, end_slider = compare_subinterval_with_neighbours(
                        [start_slider, end_slider], domain, index
                    )

                    all_sliders[index][0] = start_slider
                    all_sliders[index][1] = end_slider
                    if minim >= cur_slider_arr[0]:
                        all_sliders[index][2] = np.floor(cur_slider_arr[0])
                    if maxim <= cur_slider_arr[1]:
                        all_sliders[index][3] = np.ceil(cur_slider_arr[1])
                    st.rerun()

                if start_input != cur_slider_arr[0] or end_input != cur_slider_arr[1]:
                    start_input, end_input = compare_subinterval_with_neighbours(
                        [start_input, end_input], domain, index
                    )
                    all_sliders[index][0] = start_input
                    all_sliders[index][1] = end_input
                    if minim >= cur_slider_arr[0]:
                        all_sliders[index][2] = np.floor(cur_slider_arr[0])
                    if maxim <= cur_slider_arr[1]:
                        all_sliders[index][3] = np.ceil(cur_slider_arr[1])
                    st.rerun()

                if minim != cur_slider_arr[2] and minim <= cur_slider_arr[0]:
                    all_sliders[index][2] = minim
                    st.rerun()
                if maxim != cur_slider_arr[3] and maxim >= cur_slider_arr[1]:
                    all_sliders[index][3] = maxim
                    st.rerun()

            all_sliders = get_slider_domain_value(domain)
            for index in range(get_sliders_size(domain)):
                cur_slider_arr = all_sliders[index]
                x_slider, x_start_end, x_min_max = st.columns([7, 2, 2])
                with x_slider:
                    st.session_state["x_slider_" + domain + "_index_" + str(index)] = (
                        cur_slider_arr[0],
                        cur_slider_arr[1],
                    )
                    start_slider, end_slider = cast(
                        tuple[int, int],
                        st.slider(
                            "Select interval",
                            min_value=cur_slider_arr[2],
                            max_value=cur_slider_arr[3],
                            key="x_slider_" + domain + "_index_" + str(index),
                        ),
                    )
                with x_start_end:
                    st.session_state[
                        "x_interval_STR_number_input_" + domain + "_index_" + str(index)
                    ] = cur_slider_arr[0]
                    start_input = st.number_input(
                        "Start x",
                        # value=cur_slider_arr[0],
                        # min_value=cur_slider_arr[2],max_value=cur_slider_arr[1],
                        step=1.0,
                        format="%.2f",
                        key="x_interval_STR_number_input_"
                        + domain
                        + "_index_"
                        + str(index),
                    )
                    st.session_state[
                        "x_interval_END_number_input_" + domain + "_index_" + str(index)
                    ] = cur_slider_arr[1]
                    end_input = st.number_input(
                        "End x",
                        # value=cur_slider_arr[1],
                        # min_value=cur_slider_arr[0],max_value=cur_slider_arr[3],
                        step=1.0,
                        key="x_interval_END_number_input_"
                        + domain
                        + "_index_"
                        + str(index),
                    )

                with x_min_max:
                    st.session_state[
                        "x_interval_MIN_number_input_" + domain + "_index_" + str(index)
                    ] = cur_slider_arr[2]

                    minim = st.number_input(
                        "Minimum x",
                        # value=cur_slider_arr[2],
                        # max_value=cur_slider_arr[0],
                        step=1.0,
                        key="x_interval_MIN_number_input_"
                        + domain
                        + "_index_"
                        + str(index),
                    )
                    st.session_state[
                        "x_interval_MAX_number_input_" + domain + "_index_" + str(index)
                    ] = cur_slider_arr[3]
                    maxim = st.number_input(
                        "Maximum x",
                        # value=cur_slider_arr[3],
                        # min_value=cur_slider_arr[1],
                        step=1.0,
                        key="x_interval_MAX_number_input_"
                        + domain
                        + "_index_"
                        + str(index),
                    )

    return st.session_state["x_intervals_input_" + domain]


def compare_subinterval_with_neighbours(cur_inter, domain, index):
    if cur_inter[0] > cur_inter[1]:
        return compare_subinterval_with_neighbours(
            [cur_inter[1], cur_inter[0]], domain, index
        )
    if index > 0:
        prev_arr = get_slider_values(domain, index - 1)
        # check if start and end is larger than prev end

        if prev_arr[1] > cur_inter[0]:
            return compare_subinterval_with_neighbours(
                [prev_arr[1], cur_inter[1]], domain, index
            )
    if index < get_sliders_size(domain) - 1:
        # check if start and end is smaller than next start
        next_arr = get_slider_values(domain, index + 1)
        # check if start and end is larger than prev end

        if next_arr[0] < cur_inter[1]:
            return compare_subinterval_with_neighbours(
                [cur_inter[0], next_arr[0]], domain, index
            )
        pass
    return cur_inter


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


LGROUP_F = 1
LGROUP_INTERMEDIATE = 2
LGROUP_SIDES = 3
LGROUP_BASE = 4


def dictionary_inherit(child, parent):
    for key in parent:
        if key in child:
            if isinstance(child[key], dict) and isinstance(parent[key], dict):
                dictionary_inherit(child[key], parent[key])
        else:
            child[key] = parent[key]

    return child


BASE_COLOR_OLD = "#252422"
BASE_COLOR = "#4287f5"
LINE_COLOR = "#000000"

current_theme = st.context.theme.type
if current_theme == "light":
    F_COLOR = "#eb5e28"
    SIDES_COLOR = "#403d39"
else:
    F_COLOR = "#fc6f39"
    SIDES_COLOR = "#ffffff"

PTLY_MESH_DEF = dict(
    opacity=1.0,
    color="#FFFFFF",
    hoverinfo="x+y+z",
)

PTLY_MINOR_GRID_DEF = dict(
    opacity=1,
    mode="lines",
    line=dict(color="#000000", dash="dash", width=1.2, shape="spline"),
    hoverinfo="x+y+z",
)

PTLY_MAJOR_GRID_DEF = dict(
    opacity=1,
    mode="lines",
    line=dict(color="#000000", width=2.5, shape="spline"),
    hoverinfo="x+y+z",
)

PTLY_F_MESH_DEF = dict(
    color=F_COLOR,
)
dictionary_inherit(PTLY_F_MESH_DEF, PTLY_MESH_DEF)


PTLY_F_MINOR_GRID_DEF = dict(
    line=dict(color=LINE_COLOR),
)
dictionary_inherit(PTLY_F_MINOR_GRID_DEF, PTLY_MINOR_GRID_DEF)


PTLY_F_MAJOR_GRID_DEF = dict(line=dict(color=F_COLOR), name="Function curve")
dictionary_inherit(PTLY_F_MAJOR_GRID_DEF, PTLY_MAJOR_GRID_DEF)


PTLY_F_PACKAGE_SPEC = dict(
    spec=PTLY_F_MESH_DEF,
    minor_spec=PTLY_F_MINOR_GRID_DEF,
    major_spec=PTLY_F_MAJOR_GRID_DEF,
)


PTLY_BASE_MESH_DEF = dict(
    color=BASE_COLOR,
)
dictionary_inherit(PTLY_BASE_MESH_DEF, PTLY_MESH_DEF)


PTLY_BASE_MINOR_GRID_DEF = dict(
    line=dict(color=LINE_COLOR),
)
dictionary_inherit(PTLY_BASE_MINOR_GRID_DEF, PTLY_MINOR_GRID_DEF)


PTLY_BASE_MAJOR_GRID_DEF = dict(line=dict(color=BASE_COLOR), name="Integral Base")
dictionary_inherit(PTLY_BASE_MAJOR_GRID_DEF, PTLY_MAJOR_GRID_DEF)

PTLY_BASE_PACKAGE_SPEC = dict(
    spec=PTLY_BASE_MESH_DEF,
    minor_spec=PTLY_BASE_MINOR_GRID_DEF,
    major_spec=PTLY_BASE_MAJOR_GRID_DEF,
)


PTLY_SIDES_MESH_DEF = dict(
    color=SIDES_COLOR,
)
dictionary_inherit(PTLY_SIDES_MESH_DEF, PTLY_MESH_DEF)


PTLY_SIDES_MINOR_GRID_DEF = dict(
    line=dict(color=SIDES_COLOR), name="Intermediate curves"
)
dictionary_inherit(PTLY_SIDES_MINOR_GRID_DEF, PTLY_MINOR_GRID_DEF)


PTLY_SIDES_MAJOR_GRID_DEF = dict(
    line=dict(color=SIDES_COLOR),
    name="Boundary Curves",
)
dictionary_inherit(PTLY_SIDES_MAJOR_GRID_DEF, PTLY_MAJOR_GRID_DEF)


PTLY_SIDES_PACKAGE_SPEC = dict(
    spec=PTLY_SIDES_MESH_DEF,
    minor_spec=PTLY_SIDES_MINOR_GRID_DEF,
    major_spec=PTLY_SIDES_MAJOR_GRID_DEF,
)


st.set_page_config(layout="wide")


def on_2D_Tab_change():
    # the value in st.session_state["2DTabs"] is the new tab
    # Disable auto generate on all graphs
    # If a tab was toggled then make current tab toggled
    all_tabs = [
        "Cavalieri Input",
        "Riemann-Stieltjes Input",
        "Quadrilateral Strips Input",
        "Config",
    ]
    toggle_keys = ["gen_toggle_Cav", "gen_toggle_RiS", "gen_toggle_QuS"]
    was_toggled = False

    if st.session_state["2DTabs"] == all_tabs[-1]:
        return

    for key in toggle_keys:
        was_toggled = was_toggled or st.session_state[key]
        st.session_state[key] = False

        if was_toggled:
            for i in range(len(all_tabs[:-1])):
                if st.session_state["2DTabs"] == all_tabs[i]:
                    st.session_state[toggle_keys[i]] = True
                    st.session_state[toggle_keys[i] + "_persistent"] = True
                    break


def input_tab_section(
    f_default,
    cg_label,
    cg_default,
    cg_vars,
    disp_func,
):
    st.subheader("Function selection")
    f_label_col, f_input_col, cg_label_col, cg_input_col = st.columns([1, 5, 1, 5])

    with f_label_col:
        st.write("###")
        st.latex("f(x)=")

    with f_input_col:
        f_sym_input = math_input_component(
            key="f_sym_input_" + domain, value=f_default, variables="x"
        )
        # eg variables="xyz"
        show_f_latex_button = st.toggle(
            "Show equation details", key="show_f_latex_button_" + domain, value=False
        )

        with st.expander("Latex", expanded=show_f_latex_button):
            st.code(f_sym_input, language="latex")

    with cg_label_col:
        st.write("###")
        st.latex(cg_label)

    with cg_input_col:
        cg_sym_input = math_input_component(
            key="cg_input_" + domain + "_field", value=cg_default, variables=cg_vars
        )
        # eg variables="xyz"
        if cg_sym_input == None:
            cg_sym_input = ""
        show_cg_latex_button = st.toggle(
            "Show equation details", key="show_cg_latex_button_" + domain, value=False
        )

        with st.expander("Latex", expanded=show_cg_latex_button):
            st.code(cg_sym_input, language="latex")

    x_intervals_input = x_interval_section(domain)

    gen_button_and_toggle, _ = st.columns([5, 7])

    with gen_button_and_toggle:
        gen_button_col, gen_toggle_col = st.columns([2, 4])

        gen_toggle = False

        if "gen_toggle_" + domain + "_persistent" not in st.session_state:
            st.session_state["gen_toggle_" + domain + "_persistent"] = False
        with gen_toggle_col:
            if "gen_toggle_" + domain in st.session_state:
                gen_toggle = st.toggle("Auto Generate", key="gen_toggle_" + domain)
            else:
                gen_toggle = st.toggle(
                    "Auto Generate",
                    key="gen_toggle_" + domain,
                    value=st.session_state["gen_toggle_" + domain + "_persistent"],
                )
        with gen_button_col:
            gen_button = st.button(
                "Generate", key="gen_button_" + domain, disabled=gen_toggle
            )
        gen_toggle = gen_toggle or gen_button
        st.session_state["gen_toggle_" + domain + "_persistent"] = gen_toggle

    if gen_toggle:
        f_expr = str(f_sym_input)
        cg_expr = str(cg_sym_input)
        intervals_expr = str(x_intervals_input)
        try:
            displays = disp_func(
                f_expr,
                cg_expr,
                intervals_expr,
                True,
                x_res2d,
                y_res2d,
                interm_cs,
                rf_iters,
                integ_iters,
                tol,
            )
            return displays
        except Exception as ex:
            st.error(f"⚠️ An error has occurred: {ex}")


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def check_display_format(displays):
    def is_cav_and_rs_2d():
        if not hasattr(displays, "__iter__"):
            return False

        required_attrs = ["integ_value", "a", "b", "xv", "fv", "gv", "dgv", "cvs"]
        for d in displays:
            actual_attrs = {attr for attr in dir(d) if not attr.startswith("__")}
            if actual_attrs != set(required_attrs):
                return False
        return True

    def is_quad_strips_2d():
        # TODO: for now if not Cav and RS then Quad
        return True

    if is_cav_and_rs_2d():
        return DisplayFormat.CAVALIERI_RIEMANN_INT
    elif is_quad_strips_2d():
        return DisplayFormat.QUADRILATERAL_STRIPS
    else:
        return DisplayFormat.OTHER


def plot_cav_and_rs_2D(displays):
    cav_integ_fig = make_subplots(
        2,
        2,
        shared_xaxes="all",
        shared_yaxes="all",
        subplot_titles=("Cavalieri Integral", "f(h(x))", "f(x*)g'(x*)"),
        horizontal_spacing=0.05,
        vertical_spacing=0.1,
    )
    cav_integ_fig["layout"]["xaxis2_showticklabels"] = True
    cav_integ_fig["layout"]["height"] = 800
    cav_integ_fig.update_annotations(font_size=24)

    g_graphs_fig = make_subplots(
        2,
        1,
        shared_xaxes=True,
        subplot_titles=("g(x*)", "g'(x*)"),
        vertical_spacing=0.1,
    )
    g_graphs_fig["layout"]["height"] = 800
    g_graphs_fig.update_annotations(font_size=24)

    cav_f = []
    cav_base = []
    cav_inter = []
    cav_sides = []
    rs_f = []
    rs_base = []
    rs_inter = []
    rs_sides = []
    r_f = []
    r_base = []
    r_inter = []
    r_sides = []
    lg_i = 0
    interval_integ_df = []
    accu_sum = 0.0
    accu_err = 0.0
    for display in displays:
        iv, ierr = display.integ_value
        accu_sum += iv
        accu_err += ierr

        interval_integ_df.append([f"[{display.a:.2e}, {display.b:.2e}]", iv, ierr])
        xv = np.array(display.xv)
        fv = np.array(display.fv)
        gv = np.array(display.gv)
        dgv = np.array(display.dgv)
        cvs = display.cvs
        for i in range(len(cvs)):
            index, cv = cvs[i]
            cvs[i] = (index, np.array(cv))
        lg_i += 1
        group_title = f"[{xv[0]:.2e}, {xv[-1]:.2e}]"
        spec_f = dictionary_inherit(
            dict(legendgroup=f"f{lg_i}", legendgrouptitle=dict(text=group_title)),
            PTLY_F_MAJOR_GRID_DEF,
        )
        spec_base = dictionary_inherit(
            dict(
                legendgroup=f"f{lg_i}",
                legendgrouptitle=dict(text=group_title),
            ),
            PTLY_BASE_MAJOR_GRID_DEF,
        )
        spec_sides = dictionary_inherit(
            dict(legendgroup=f"f{lg_i}", legendgrouptitle=dict(text=group_title)),
            PTLY_SIDES_MAJOR_GRID_DEF,
        )
        spec_inter = dictionary_inherit(
            dict(legendgroup=f"f{lg_i}", legendgrouptitle=dict(text=group_title)),
            PTLY_SIDES_MINOR_GRID_DEF,
        )

        make_legend = True
        # Intermediate c(y) graphs
        for i in range(1, len(cvs) - 1):
            _, cv = cvs[i]
            cav_inter.append(
                go.Scatter(x=cv[:, 1], y=cv[:, 0], showlegend=make_legend, **spec_inter)
            )
            make_legend = False

        # R x {0}
        cav_base.append(
            go.Scatter(x=gv, y=np.zeros_like(gv), showlegend=True, **spec_base)
        )

        # Boundary curve at `a`
        _, cv = cvs[0]
        cav_sides.append(
            go.Scatter(x=cv[:, 1], y=cv[:, 0], showlegend=True, **spec_sides)
        )

        # Boundary curve at `b`
        _, cv = cvs[-1]
        cav_sides.append(
            go.Scatter(x=cv[:, 1], y=cv[:, 0], showlegend=False, **spec_sides)
        )

        # S x f(S)
        cav_f.append(go.Scatter(x=xv, y=fv, showlegend=True, **spec_f))

        # Equivalent Riemann-Stieltjes integral over S.

        # f(S)*g'(S)
        rs_f.append(go.Scatter(x=xv, y=fv * dgv, showlegend=False, **spec_f))

        # Intermediate graphs
        for i in range(1, len(cvs) - 1):
            xindex, _ = cvs[i]
            rs_inter.append(
                go.Scatter(
                    x=xv[[xindex, xindex]],
                    y=[0, fv[xindex] * dgv[xindex]],
                    showlegend=False,
                    **spec_inter,
                )
            )

        # Boundary at `a`
        rs_sides.append(
            go.Scatter(
                x=xv[[0, 0]], y=[0, fv[0] * dgv[0]], showlegend=False, **spec_sides
            )
        )

        # Boundary at `b`
        rs_sides.append(
            go.Scatter(
                x=xv[[-1, -1]], y=[0, fv[-1] * dgv[-1]], showlegend=False, **spec_sides
            )
        )

        # Base
        rs_base.append(
            go.Scatter(x=xv, y=np.zeros_like(xv), showlegend=False, **spec_base)
        )

        # Equivalent Riemann integral over R.

        # f(h(R))
        r_f.append(go.Scatter(x=gv, y=fv, showlegend=False, **spec_f))

        # Intermediate graphs
        for i in range(1, len(cvs) - 1):
            xindex, _ = cvs[i]
            r_inter.append(
                go.Scatter(
                    x=gv[[xindex, xindex]],
                    y=[0, fv[xindex]],
                    showlegend=False,
                    **spec_inter,
                )
            )

        # Boundary at `g(a)`
        r_sides.append(
            go.Scatter(
                x=gv[[0, 0]],
                y=[0, fv[0]],
                showlegend=False,
                **spec_sides,
            )
        )

        # Boundary at `g(b)`
        r_sides.append(
            go.Scatter(x=gv[[-1, -1]], y=[0, fv[-1]], showlegend=False, **spec_sides)
        )

        # Base
        r_base.append(
            go.Scatter(x=gv, y=np.zeros_like(gv), showlegend=False, **spec_base)
        )

        # Miscellaneous graphs

        # g graph
        g_graphs_fig.add_trace(
            go.Scatter(
                x=xv,
                y=gv,
                **PTLY_F_MAJOR_GRID_DEF,
                showlegend=True,
                legendgroup=f"f{lg_i}",
                legendgrouptitle=dict(text=group_title),
            ),
            row=1,
            col=1,
        )

        # dg graph
        g_graphs_fig.add_trace(
            go.Scatter(
                x=xv,
                y=dgv,
                **PTLY_F_MAJOR_GRID_DEF,
                showlegend=False,
                legendgroup=f"f{lg_i}",
            ),
            row=2,
            col=1,
        )

    interval_integ_df.append(["Total", accu_sum, accu_err])
    interval_integ_df = pd.DataFrame(
        interval_integ_df,
        columns=["Interval", "Integration Value", "Estimated Error"],
        index=None,
    )

    cav_integ_fig.add_traces(cav_inter + cav_sides + cav_base + cav_f, 1, 1)
    cav_integ_fig.add_traces(rs_inter + rs_sides + rs_base + rs_f, 2, 1)
    cav_integ_fig.add_traces(r_inter + r_sides + r_base + r_f, 1, 2)

    cav_int_tab, misc_graph_tab, integ_tab = st.tabs(
        ["Integral Graphs", "Misc Graphs", "Interval Integration Values"]
    )

    with cav_int_tab:
        if cav_integ_fig:
            st.plotly_chart(cav_integ_fig, width="stretch")

    with misc_graph_tab:
        if g_graphs_fig:
            st.plotly_chart(g_graphs_fig, width="stretch")

    with integ_tab:
        st.dataframe(
            interval_integ_df.style.format(
                "{:.4e}", subset=["Integration Value", "Estimated Error"]
            ),
            width="stretch",
        )


def plot_quad_strips_2D(displays):

    quad_integ_fig = make_subplots(
        2,
        2,
        shared_xaxes="all",
        shared_yaxes="all",
        subplot_titles=(
            "Quadrilateral Strips",
            "",
            "1/2 * f(x)+f′(x)(g(x) − x)dx",
            "1/2 * f(x)dg(x)",
        ),
        horizontal_spacing=0.05,
        vertical_spacing=0.1,
    )
    quad_integ_fig["layout"]["xaxis2_showticklabels"] = True
    quad_integ_fig["layout"]["height"] = 800
    quad_integ_fig.update_annotations(font_size=24)

    # Make misc graphs relevent
    cav_and_rs_graphs_fig = make_subplots(
        2,
        2,
        shared_xaxes=True,
        subplot_titles=("Cavalieri", "Riemann-Stieltjes", "l1", "l2"),
        vertical_spacing=0.1,
    )
    cav_and_rs_graphs_fig["layout"]["height"] = 800
    cav_and_rs_graphs_fig.update_annotations(font_size=24)

    qs_inter = []
    qs_sides = []
    qs_base = []
    qs_f = []

    s1_inter = []
    s1_sides = []
    s1_base = []
    s1_f = []

    s2_inter = []
    s2_sides = []
    s2_base = []
    s2_f = []

    l1_f = []
    l1_base = []
    l1_inter = []
    l1_sides = []

    l2_f = []
    l2_base = []
    l2_inter = []
    l2_sides = []

    cav_f = []
    cav_base = []
    cav_inter = []
    cav_sides = []

    rs_f = []
    rs_base = []
    rs_inter = []
    rs_sides = []

    lg_i = 0
    interval_integ_df = []
    accu_sum = 0.0
    accu_err = 0.0

    x_min = 0
    x_max = 0
    y_min = -0.01
    y_max = 0.01
    for display in displays:
        iv, ierr = display.integ_value
        accu_sum += iv
        accu_err += ierr

        interval_integ_df.append([f"[{display.a:.2e}, {display.b:.2e}]", iv, ierr])
        xv = np.array(display.xv)
        fv = np.array(display.fv)
        gv = np.array(display.gv)
        # dgv = np.array(display.dgv)
        cvs = display.cvs

        l1 = np.array(display.l1)
        l2 = np.array(display.l2)

        for i in range(len(cvs)):
            index, cv = cvs[i]
            cvs[i] = (index, np.array(cv))
        lg_i += 1
        group_title = f"[{xv[0]:.2e}, {xv[-1]:.2e}]"
        spec_f = dictionary_inherit(
            dict(legendgroup=f"f{lg_i}", legendgrouptitle=dict(text=group_title)),
            PTLY_F_MAJOR_GRID_DEF,
        )
        spec_base = dictionary_inherit(
            dict(
                legendgroup=f"f{lg_i}",
                legendgrouptitle=dict(text=group_title),
            ),
            PTLY_BASE_MAJOR_GRID_DEF,
        )
        spec_sides = dictionary_inherit(
            dict(legendgroup=f"f{lg_i}", legendgrouptitle=dict(text=group_title)),
            PTLY_SIDES_MAJOR_GRID_DEF,
        )
        spec_inter = dictionary_inherit(
            dict(legendgroup=f"f{lg_i}", legendgrouptitle=dict(text=group_title)),
            PTLY_SIDES_MINOR_GRID_DEF,
        )

        make_legend = True
        # Intermediate c(y) graphs
        for i in range(1, len(cvs) - 1):
            _, cv = cvs[i]
            cav_inter.append(
                go.Scatter(x=cv[:, 1], y=cv[:, 0], showlegend=make_legend, **spec_inter)
            )
            make_legend = False

        # R x {0}
        cav_base.append(
            go.Scatter(x=gv, y=np.zeros_like(gv), showlegend=True, **spec_base)
        )

        # Boundary curve at `a`
        _, cv = cvs[0]
        cav_sides.append(
            go.Scatter(x=cv[:, 1], y=cv[:, 0], showlegend=True, **spec_sides)
        )

        # Boundary curve at `b`
        _, cv = cvs[-1]
        cav_sides.append(
            go.Scatter(x=cv[:, 1], y=cv[:, 0], showlegend=False, **spec_sides)
        )

        # S x f(S)
        cav_f.append(go.Scatter(x=xv, y=fv, showlegend=True, **spec_f))

        # Intermediate graphs
        # Equivalent Riemann-Stieltjes integral over S.
        # f(h(R))
        rs_f.append(go.Scatter(x=gv, y=fv, showlegend=False, **spec_f))

        # Intermediate graphs
        for i in range(1, len(cvs) - 1):
            xindex, _ = cvs[i]
            rs_inter.append(
                go.Scatter(
                    x=gv[[xindex, xindex]],
                    y=[0, fv[xindex]],
                    showlegend=False,
                    **spec_inter,
                )
            )

        # Boundary at `g(a)`
        rs_sides.append(
            go.Scatter(
                x=gv[[0, 0]],
                y=[0, fv[0]],
                showlegend=False,
                **spec_sides,
            )
        )

        # Boundary at `g(b)`
        rs_sides.append(
            go.Scatter(x=gv[[-1, -1]], y=[0, fv[-1]], showlegend=False, **spec_sides)
        )

        # Base
        rs_base.append(
            go.Scatter(x=gv, y=np.zeros_like(gv), showlegend=False, **spec_base)
        )

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Quadrilateral strips integral
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        qs_base.append(
            go.Scatter(x=gv, y=np.zeros_like(gv), showlegend=False, **spec_base)
        )
        top_x = [cv[1][-1, 1] for cv in cvs]
        top_y = [cv[1][-1, 0] for cv in cvs]
        qs_f.append(go.Scatter(x=top_x, y=top_y, showlegend=False, **spec_f))
        for i in range(1, len(cvs) - 1):
            _, cv = cvs[i]
            qs_inter.append(
                go.Scatter(
                    x=cv[[0, -1], 1], y=cv[[0, -1], 0], showlegend=False, **spec_inter
                )
            )
        for i in [0, -1]:
            _, cv = cvs[i]
            qs_sides.append(
                go.Scatter(
                    x=cv[[0, -1], 1], y=cv[[0, -1], 0], showlegend=False, **spec_sides
                )
            )

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Inbetween sum graphs
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        fv_arr = np.asarray(fv, dtype=float)
        s1_arr = np.asarray(l1, dtype=float)
        s2_arr = np.asarray(l2, dtype=float)
        lsum = s1_arr + s2_arr
        eps = 1e-12

        s1_qs = np.empty_like(fv_arr)
        s2_qs = np.empty_like(fv_arr)

        mask = np.abs(lsum) > eps

        s1_qs[mask] = fv_arr[mask] * (s1_arr[mask] / lsum[mask])
        s2_qs[mask] = fv_arr[mask] * (s2_arr[mask] / lsum[mask])

        s1_qs[~mask] = 0.5 * fv_arr[~mask]
        s2_qs[~mask] = 0.5 * fv_arr[~mask]

        s1_base.append(
            go.Scatter(x=xv, y=np.zeros_like(xv), showlegend=False, **spec_base)
        )

        s1_f.append(go.Scatter(x=xv, y=s1_qs, showlegend=False, **spec_f))

        for i in range(1, len(cvs) - 1):
            idx, _ = cvs[i]

            s1_inter.append(
                go.Scatter(
                    x=[xv[idx], xv[idx]],
                    y=[0, s1_qs[idx]],
                    showlegend=False,
                    **spec_inter,
                )
            )

        for i in [0, -1]:
            idx, _ = cvs[i]

            s1_sides.append(
                go.Scatter(
                    x=[xv[idx], xv[idx]],
                    y=[0, s1_qs[idx]],
                    showlegend=False,
                    **spec_sides,
                )
            )

        s2_base.append(
            go.Scatter(x=gv, y=np.zeros_like(gv), showlegend=False, **spec_base)
        )

        s2_f.append(go.Scatter(x=xv, y=s2_qs, showlegend=False, **spec_f))
        s2_base.append(
            go.Scatter(x=gv, y=np.zeros_like(gv), showlegend=False, **spec_base)
        )

        s2_f.append(go.Scatter(x=xv, y=s2_qs, showlegend=False, **spec_f))
        for i in range(1, len(cvs) - 1):
            idx, cv = cvs[i]

            s2_inter.append(
                go.Scatter(
                    x=cv[:, 1],
                    y=cv[:, 0] * (s2_qs[idx] / fv[idx]),
                    showlegend=False,
                    **spec_inter,
                )
            )
        for i in [0, -1]:
            idx, cv = cvs[i]
            s2_sides.append(
                go.Scatter(
                    x=cv[:, 1],
                    y=cv[:, 0] * (s2_qs[idx] / fv[idx]),
                    showlegend=False,
                    **spec_sides,
                )
            )

        l1_f.append(go.Scatter(x=xv, y=l1, showlegend=False, **spec_f))

        l2_f.append(go.Scatter(x=xv, y=l2, showlegend=False, **spec_f))

        x_min = min(x_min, np.min(xv), np.min(gv))
        x_max = max(x_max, np.max(xv), np.max(gv))
        for _, cv in cvs:
            x_min = min(x_min, np.min(cv[:, 1]))
            x_max = max(x_max, np.max(cv[:, 1]))

        y_min = min(y_min, np.min(fv), np.min(s1_qs), np.min(s2_qs))
        y_max = max(y_max, np.max(fv), np.max(s1_qs), np.max(s2_qs))

        quad_integ_fig.add_traces(qs_f + qs_base + qs_sides + qs_inter, 1, 1)
        quad_integ_fig.add_traces(s1_f + s1_base + s1_sides + s1_inter, 2, 1)
        quad_integ_fig.add_traces(s2_f + s2_base + s2_sides + s2_inter, 2, 2)
    interval_integ_df.append(["Total", accu_sum, accu_err])
    interval_integ_df = pd.DataFrame(
        interval_integ_df,
        columns=["Interval", "Integration Value", "Estimated Error"],
        index=None,
    )

    quad_integ_fig.update_xaxes(range=[x_min, x_max])
    quad_integ_fig.update_yaxes(range=[y_min, y_max])

    # Miscellaneous graphs
    # Cavalieri
    cav_and_rs_graphs_fig.add_traces(cav_inter + cav_sides + cav_base + cav_f, 1, 1)
    # Riemann-Stieltes graph
    cav_and_rs_graphs_fig.add_traces(rs_inter + rs_sides + rs_base + rs_f, 1, 2)

    # l1
    cav_and_rs_graphs_fig.add_traces(l1_f + l1_base + l1_sides + l1_inter, 2, 1)
    # l2
    cav_and_rs_graphs_fig.add_traces(l2_f + l2_base + l2_sides + l2_inter, 2, 2)

    quad_int_tab, misc_graph_tab, integ_tab = st.tabs(
        ["Integral Graphs", "Misc Graphs", "Interval Integration Values"]
    )

    with quad_int_tab:
        if quad_integ_fig:
            st.plotly_chart(quad_integ_fig, width="stretch")

    with misc_graph_tab:
        if cav_and_rs_graphs_fig:
            st.plotly_chart(cav_and_rs_graphs_fig, width="stretch")

    with integ_tab:
        st.dataframe(
            interval_integ_df.style.format(
                "{:.4e}", subset=["Integration Value", "Estimated Error"]
            ),
            width="stretch",
        )


input_cav_tab, input_rs_tab, input_qs_tab, config_tab = st.tabs(
    [
        "Cavalieri Input",
        "Riemann-Stieltjes Input",
        "Quadrilateral Strips Input",
        "Config",
    ],
    key="2DTabs",
    on_change=on_2D_Tab_change,
)

with config_tab:

    st.write("# Config")
    x_res2d = st.number_input(
        "X Resolution",
        help="Sets the x resolution for each produced interval.",
        key="cfg2d_x_res",
        min_value=50,
        max_value=500,
        value=100,
    )

    y_res2d = st.number_input(
        "Y Resolution",
        help="Sets the y resolution for each produced interval.",
        key="cfg2d_y_res",
        min_value=50,
        max_value=500,
        value=100,
    )

    interm_cs = st.number_input(
        "Intermediate Curves",
        help="How many intermediate c_x(y) curves to plot.",
        key="cfg2d_interm_cs",
        min_value=0,
        max_value=20,
        value=4,
    )

    rf_iters = st.number_input(
        "Maximum Root Finding Iterations",
        help="Sets the maximum root finding iterations before failure.",
        key="cfg2d_rf_iters",
        min_value=10,
        max_value=1000,
        value=100,
    )

    integ_iters = st.number_input(
        "Maximum Integration Iterations",
        help="Sets the maximum adaptive Gauss-Kronrod iterations before failure.",
        key="cfg2d_integ_iters",
        min_value=10,
        max_value=1000,
        value=100,
    )

    tol = 10 ** st.number_input(
        "Integration Tolerance Base 10 Exponent",
        help="Sets the absolute integration tolerance exponent.",
        key="cfg2d_tol",
        min_value=-12,
        max_value=-5,
        value=-9,
    )


displays = None


with input_cav_tab:
    domain = "Cav"
    st.write("# Parameters for Cavalieri integral")

    f_default = "\\frac{x}{2}+0.5"
    cg_label = "c(y)="
    cg_default = "-y^2"
    cg_vars = "y"
    disp_func = display_cav2d

    cav_displays = input_tab_section(
        f_default,
        cg_label,
        cg_default,
        cg_vars,
        disp_func,
    )
    if cav_displays != None:
        displays = cav_displays

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

with input_rs_tab:
    domain = "RiS"
    st.write("# Parameters for Riemann-Stieltjes integral")

    f_default = "\\frac{x}{2}+0.1"
    cg_label = "g(x)="
    cg_default = "\\sin(x)"
    cg_vars = "x"
    disp_func = display_cav2d_rs

    ris_displays = input_tab_section(
        f_default,
        cg_label,
        cg_default,
        cg_vars,
        disp_func,
    )
    if ris_displays != None:
        displays = ris_displays

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

with input_qs_tab:
    domain = "QuS"
    st.write("# Parameters for Quadrilateral Strips integral")

    f_default = "\\frac{x+0.5}{2}"
    cg_label = "g(x)="
    cg_default = "\\left(x+0.25\\right)^2"
    cg_vars = "x"
    disp_func = display_cav2d_qs

    qus_displays = input_tab_section(
        f_default,
        cg_label,
        cg_default,
        cg_vars,
        disp_func,
    )
    if qus_displays != None:
        displays = qus_displays


if (
    "displays" in locals()
    and displays != None
    and not st.session_state["2DTabs"] == "Config"
):
    match check_display_format(displays):
        case DisplayFormat.CAVALIERI_RIEMANN_INT:
            plot_cav_and_rs_2D(displays)
        case DisplayFormat.QUADRILATERAL_STRIPS:
            plot_quad_strips_2D(displays)
        case DisplayFormat.OTHER:
            pass
        case _:
            pass
