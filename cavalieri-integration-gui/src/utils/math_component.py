import streamlit.components.v1 as components
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
build_dir = os.path.join(current_dir, "math_component")

_math_input_func = components.declare_component("math_input", path=build_dir)

def math_input_component(key=None,value=None, variables=None, changeVal=False):
    return _math_input_func(key=key, value=value, variables=variables, changeVal=changeVal)
