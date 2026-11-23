# import ast
# import streamlit as st
#
# # import streamlit.components.v1 as components
# from enum import Enum, auto
# from typing import cast
#
#
# from cavint import display_cav2d, display_cav2d_rs, display_cav2d_qs
# from utils.math_component import math_input_component
#

import numpy as np

# from plotly.subplots import make_subplots
# import plotly.graph_objects as go
# import pandas as pd

import streamlit as st

# from cavint import display_cav2d
from cavint import display_cav2d, display_cav2d_rs, display_cav2d_qs


def dictionary_inherit(child, parent):
    for key, value in parent.items():
        if key not in child:
            child[key] = value
        elif isinstance(child[key], dict) and isinstance(value, dict):
            dictionary_inherit(child[key], value)
    return child


import plotly.graph_objects as go
from plotly.subplots import make_subplots

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


st.set_page_config(page_title="Cavalieri Integration", layout="wide")


def main():
    st.write("# Cavalieri Integration and Quadrilateral strips")

    HOME_TEXT = r"""
    Cavalieri Integration in $\mathbb{R}^n$ presents a novel visualization mechanism for weighted integration 
    and challenges the notion of strictly rectangular integration strips. It does so by concealing the integrator
    inside the boundary curves of the integral. This sandbox allows the user to create visualizations of this
    integral in $\mathbb{R}^2$ and $\mathbb{R}^3$ as well as creating Cavalieri integral representations for
    the Riemann-Stieltjes integral.

    The sandbox also implements the quadrilateral integration strips to investigate the use of the new integral.
    """

    st.write(HOME_TEXT)

    st.subheader("From weighted integration to quadrilateral strips")
    st.write(
        "The four graphs below use the same functions and interval. The first "
        "three show representations of the same weighted integral; the fourth "
        "uses straight strip boundaries to construct the quadrilateral-strips integral."
    )
    st.latex(r"f(x)=\frac{x}{2}+0.1,\qquad g(x)=\sin(x),\qquad x\in[0,1.5]")
    st.caption(
        "Orange shows the function f(x), blue shows the base, and the other lines "
        "show strip boundaries. Hover over a graph for coordinates, or drag to zoom."
    )

    f_expr = "\\frac{x}{2}+0.1"
    # cg_expr = "-y^2"
    cg_expr = "sin(x)"
    intervals_expr = "[0.0,1.5]"
    x_res2d = 100
    y_res2d = 100
    interm_cs = 4
    rf_iters = 100
    integ_iters = 100
    tol = 10 ** (-9)

    displays = display_cav2d_qs(
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
    plotGraphs(displays)

    with st.expander("How the four representations relate", expanded=True):
        st.markdown(r"""
        **Riemann–Stieltjes:** The integral $I=\int_a^b f(x)\,dg(x)$ weights
        contributions by changes in $g$. The integrator malforms the function $f$ and the intervals, obscurring the effects f $g$.

        **Cavalieri:** The upper curve remains $f(x)$, while curved boundaries
        connect it to the base at $g(x)$. The geometry encodes the weighting.

        **Adjusted Riemann:** For differentiable $g$, the integral can be rewritten as 
        $I=\int_a^b f(x)g'(x)\,dx$. This graph keeps vertical boundaries and equal width intervals but
        changes the height to $f(x)g'(x)$.

        **Quadrilateral strips:** Where the Cavalieri integral connects $f(x)$ and the base with curved lines, this intergal connects $f(x)$ to
        the base with straight lines. Adjacent segments define quadrilaterals. Their limiting
        signed area is computed using the two contributions below and generally
        differs from $I$.
        """)
        st.latex(
            r"Q=\frac{1}{2}\int_{a'}^{b'}\left[f(x)+f'(x)(g(x)-x)\right]\,dx"
            r"+\frac{1}{2}\int_{a'}^{b'} f(x)\,dg(x)"
        )

    # st.subheader("Explore your own functions")
    # two_d, three_d = st.columns(2)
    # with two_d:
    #     st.page_link("pages/Display_2D.py", label="Open the 2D workspace")
    #     st.write(
    #         "Choose Cavalieri, Riemann–Stieltjes, or Quadrilateral Strips input. "
    #         "Enter functions and intervals, compare the plots, and inspect integral "
    #         "values and estimated numerical errors. Use Config to adjust resolution "
    #         "and the number of intermediate curves."
    #     )
    # with three_d:
    #     st.page_link("pages/Display_3D.py", label="Open the 3D workspace")
    #     st.write(
    #         "Explore Cavalieri regions in three dimensions. Define the function, "
    #         "boundary curves, and integration domain, then inspect the resulting surfaces."
    #     )


def plotGraphs(displays):
    rs_title, cav_title, adj_title, qs_title = st.columns([1, 1, 1, 1])

    with rs_title:
        st.text("Riemann-Stieltjes integral")
        st.latex(r"I=\int_a^b f(x)\,dg(x)")
    with cav_title:
        st.text("Cavalieri integral")
        st.latex(r"I=\int_{g(a)}^{g(b)} f(x)\,dx")
    with adj_title:
        st.text("Adjusted Riemann integral")
        st.latex(r"I=\int_a^b f(x)g'(x)\,dx")
    with qs_title:
        st.text("Quadrilateral strips integral")
        st.latex(
            "I=\\int^{a}_{b} f(x) d[g(x)] \\rightarrow \\int^{a_g(y)}_{b_g(y)} f(x) dx"
        )

    cav_integ_fig = make_subplots(
        1,
        4,
        shared_xaxes="all",
        shared_yaxes="all",
        # subplot_titles=(
        #     r"Cavalieri Integral",
        #     r"f(h(x/2))",
        #     r"f(x)g'(x)",
        # ),
        horizontal_spacing=0.05,
        vertical_spacing=0.1,
    )
    cav_integ_fig["layout"]["xaxis2_showticklabels"] = True
    cav_integ_fig["layout"]["height"] = 300
    cav_integ_fig.update_annotations(font_size=24)
    # cav_integ_fig["layout"]["top"] = 100
    cav_integ_fig.update_layout(margin=dict(t=00, b=20, l=20, r=20))

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
    accu_sum = 0.0
    accu_err = 0.0
    for display in displays:
        iv, ierr = display.integ_value
        accu_sum += iv
        accu_err += ierr

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

        make_legend = False
        # Intermediate c(y) graphs
        for i in range(1, len(cvs) - 1):
            _, cv = cvs[i]
            cav_inter.append(
                go.Scatter(x=cv[:, 1], y=cv[:, 0], showlegend=make_legend, **spec_inter)
            )
            make_legend = False

        # R x {0}
        cav_base.append(
            go.Scatter(x=gv, y=np.zeros_like(gv), showlegend=False, **spec_base)
        )

        # Boundary curve at `a`
        _, cv = cvs[0]
        cav_sides.append(
            go.Scatter(x=cv[:, 1], y=cv[:, 0], showlegend=False, **spec_sides)
        )

        # Boundary curve at `b`
        _, cv = cvs[-1]
        cav_sides.append(
            go.Scatter(x=cv[:, 1], y=cv[:, 0], showlegend=False, **spec_sides)
        )

        # S x f(S)
        cav_f.append(go.Scatter(x=xv, y=fv, showlegend=False, **spec_f))

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

    qs_inter = []
    qs_sides = []
    qs_base = []
    qs_f = []

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

    cav_integ_fig.add_traces(r_inter + r_sides + r_base + r_f, 1, 1)
    cav_integ_fig.add_traces(cav_inter + cav_sides + cav_base + cav_f, 1, 2)
    cav_integ_fig.add_traces(rs_inter + rs_sides + rs_base + rs_f, 1, 3)
    cav_integ_fig.add_traces(qs_f + qs_base + qs_sides + qs_inter, 1, 4)

    if cav_integ_fig:
        st.plotly_chart(cav_integ_fig, width="stretch")


# ~~~~~~~~~~~~~~~~~~~ Hide the Deploy button:
st.markdown(
    """
<style>
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
main()
