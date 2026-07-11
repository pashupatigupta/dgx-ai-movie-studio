import streamlit as st


DEFAULT_VALUES = {

    "prompt": "",

    "negative_prompt": "",

    "model": "SDXL",

    "width": 1024,

    "height": 1024,

    "steps": 30,

    "cfg": 8.0,

    "seed": 0

}


def initialize():

    for key, value in DEFAULT_VALUES.items():

        if key not in st.session_state:

            st.session_state[key] = value


def load_prompt(prompt):

    st.session_state.prompt = prompt["prompt"]

    st.session_state.negative_prompt = prompt["negative_prompt"]

    st.session_state.model = prompt["model"]

    st.session_state.width = prompt["width"]

    st.session_state.height = prompt["height"]

    st.session_state.steps = prompt["steps"]

    st.session_state.cfg = prompt["cfg"]

    st.session_state.seed = prompt["seed"]


def clear():

    for key, value in DEFAULT_VALUES.items():

        st.session_state[key] = value
