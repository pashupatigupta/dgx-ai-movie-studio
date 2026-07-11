"""
Enterprise Model Manager
DGX AI Movie Studio
"""

import streamlit as st
import pandas as pd

from services.model_manager_service import ModelManagerService


service = ModelManagerService()


def run():
    st.title("🤖 Enterprise Model Manager")

    st.caption(
        "Manage all AI models installed in ComfyUI"
    )

    st.divider()

    # ----------------------------------------
    # Refresh
    # ----------------------------------------

    if st.button(
        "🔄 Refresh Model Database",
        use_container_width=True
    ):

        count = service.refresh_models()

        st.success(
            f"{count} models indexed successfully."
        )

    stats = service.statistics()

    total = stats.get("total", 0) or 0
    enabled = stats.get("enabled", 0) or 0
    total_size = stats.get("total_size", 0) or 0

    disabled = total - enabled

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Models",
        total
    )

    c2.metric(
        "Enabled",
        enabled
    )

    c3.metric(
        "Disabled",
        disabled
    )

    c4.metric(
        "Disk Usage (MB)",
        round(total_size, 1)
    )

    st.divider()

    # ----------------------------------------
    # Search
    # ----------------------------------------

    keyword = st.text_input(
        "Search"
    )

    models = service.get_models()

    if keyword:

        keyword = keyword.lower()

        models = [

            m

            for m in models

            if

            keyword in m["name"].lower()

            or

            keyword in (
                m["model_type"] or ""
            ).lower()

        ]

    # ----------------------------------------
    # Filter
    # ----------------------------------------

    types = sorted(

        list(

            set(

                m["model_type"]

                for m in models

            )

        )

    )

    option = st.selectbox(

        "Model Type",

        ["All"] + types

    )

    if option != "All":

        models = [

            m

            for m in models

            if

            m["model_type"] == option

        ]

    st.divider()

    if len(models) == 0:

        st.warning(
            "No models found."
        )

        return

    table = pd.DataFrame(models)

    st.dataframe(

        table,

        use_container_width=True,

        hide_index=True

    )

st.divider()

st.subheader("Model Details")

selected = st.selectbox(

    "Select Model",

    models,

    format_func=lambda x: x["name"]

)

col1, col2 = st.columns(2)

with col1:

    st.write("### Information")

    st.write("**Name**")

    st.write(selected["name"])

    st.write("**Type**")

    st.write(selected["model_type"])

    st.write("**Folder**")

    st.write(selected["folder"])

    st.write("**Size**")

    st.write(

        round(

            selected["size_mb"],

            2

        ),

        "MB"

    )

with col2:

    st.write("### Metadata")

    tags = st.text_input(

        "Tags",

        value=selected["tags"] or ""

    )

    description = st.text_area(

        "Description",

        value=selected["description"] or ""

    )

    if st.button(

        "💾 Save Metadata"

    ):

        service.update_tags(

            selected["id"],

            tags

        )

        service.update_description(

            selected["id"],

            description

        )

        st.success(

            "Metadata Updated"

        )

st.divider()

c1, c2, c3 = st.columns(3)

with c1:

    if st.button(

        "⭐ Set Default"

    ):

        service.set_default(

            selected["id"]

        )

        st.success(

            "Default Updated"

        )

with c2:

    if selected["enabled"]:

        if st.button(

            "Disable"

        ):

            service.disable(

                selected["id"]

            )

            st.success(

                "Disabled"

            )

    else:

        if st.button(

            "Enable"

        ):

            service.enable(

                selected["id"]

            )

            st.success(

                "Enabled"

            )

with c3:

    st.write(

        "Current Status"

    )

    if selected["enabled"]:

        st.success(

            "Enabled"

        )

    else:

        st.error(

            "Disabled"

        )

    st.caption(

        f"{len(models)} models"

    )


if __name__ == "__main__":
    run()
