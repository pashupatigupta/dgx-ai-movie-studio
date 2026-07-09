import streamlit as st

def run():

    st.title("🏠 DGX AI Movie Studio")

    st.success("Enterprise AI Platform")

    c1,c2,c3,c4=st.columns(4)

    c1.metric("Models","1")

    c2.metric("Images","0")

    c3.metric("Videos","0")

    c4.metric("GPU","Ready")

    st.divider()

    st.write("""
Welcome to DGX AI Movie Studio.

Available modules:

• Image Studio

• Gallery

• Prompt Library

• GPU Dashboard

• Model Manager

• Movie Builder
""")
