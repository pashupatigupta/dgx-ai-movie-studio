import streamlit as st

def run():

    st.title("🤖 Model Manager")

    st.success("Installed Models")

    st.table({

        "Model":[

            "SDXL Base"

        ],

        "Status":[

            "Installed"

        ]

    })
