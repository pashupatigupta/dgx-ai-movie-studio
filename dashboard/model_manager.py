"""
Enterprise Model Manager
DGX AI Movie Studio
"""

import pandas as pd
import streamlit as st

from services.model_manager_service import ModelManagerService


service = ModelManagerService()


###########################################################
# Helper Functions
###########################################################

def show_statistics():

    stats = service.statistics()

    total = stats.get("total", 0) or 0
    enabled = stats.get("enabled", 0) or 0
    disabled = total - enabled
    disk = stats.get("total_size", 0) or 0

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Models", total)
    c2.metric("Enabled", enabled)
    c3.metric("Disabled", disabled)
    c4.metric("Disk (MB)", round(disk, 1))


###########################################################

def refresh_database():

    if st.button(
        "🔄 Refresh Model Database",
        use_container_width=True
    ):

        count = service.refresh_models()

        st.success(
            f"{count} models indexed."
        )

        st.rerun()


###########################################################

def search_and_filter(models):

    keyword = st.text_input(
        "🔍 Search Models"
    )

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

    return models


###########################################################

def model_table(models):

    if len(models) == 0:

        st.warning("No Models Found")

        return None

    table = pd.DataFrame(models)

    st.dataframe(

        table,

        hide_index=True,

        use_container_width=True

    )

    names = [

        model["name"]

        for model in models

    ]

    selected_name = st.selectbox(

        "Select Model",

        names

    )

    for model in models:

        if model["name"] == selected_name:

            return model

    return None


###########################################################
# Main UI
###########################################################

def run():

    st.title(
        "🤖 Enterprise Model Manager"
    )

    st.caption(
        "Manage AI Models installed in ComfyUI"
    )

    st.divider()

    refresh_database()

    show_statistics()

    st.divider()

    models = service.get_models()

    models = search_and_filter(models)

    selected = model_table(models)

    if selected is None:

        service.close()

        return
    ###########################################################
    # Model Details
    ###########################################################

    st.divider()

    st.subheader("📄 Model Details")

    col1, col2 = st.columns(2)

    with col1:

        st.text_input(
            "Model Name",
            value=selected["name"],
            disabled=True
        )

        st.text_input(
            "Model Type",
            value=selected["model_type"],
            disabled=True
        )

        st.text_input(
            "Folder",
            value=selected["folder"],
            disabled=True
        )

        st.text_input(
            "Path",
            value=selected["path"],
            disabled=True
        )

        st.text_input(
            "Size (MB)",
            value=str(round(selected["size_mb"], 2)),
            disabled=True
        )

    with col2:

        tags = st.text_input(
            "Tags",
            value=selected.get("tags") or ""
        )

        description = st.text_area(
            "Description",
            value=selected.get("description") or "",
            height=140
        )

        st.write("")

        if st.button(
            "💾 Save Metadata",
            use_container_width=True
        ):

            service.update_metadata(
                selected["id"],
                tags,
                description
            )

            st.success(
                "Metadata Updated"
            )

            st.rerun()

    ###########################################################
    # Actions
    ###########################################################

    st.divider()

    c1, c2, c3 = st.columns(3)

    with c1:

        if st.button(
            "⭐ Set Default",
            use_container_width=True
        ):

            service.set_default(
                selected["id"]
            )

            st.success(
                "Default Model Updated"
            )

            st.rerun()

    with c2:

        if selected["enabled"]:

            if st.button(
                "Disable Model",
                use_container_width=True
            ):

                service.disable(
                    selected["id"]
                )

                st.success(
                    "Model Disabled"
                )

                st.rerun()

        else:

            if st.button(
                "Enable Model",
                use_container_width=True
            ):

                service.enable(
                    selected["id"]
                )

                st.success(
                    "Model Enabled"
                )

                st.rerun()

    with c3:

        if selected["enabled"]:

            st.success("🟢 Enabled")

        else:

            st.error("🔴 Disabled")

    ###########################################################
    # Current Default
    ###########################################################

    st.divider()

    default_model = service.get_default_model()

    if default_model:

        st.info(
            f"⭐ Current Default Model: {default_model['name']}"
        )

    else:

        st.warning(
            "No default model configured."
        )

    ###########################################################
    # Model Statistics
    ###########################################################

    st.divider()

    st.subheader("📊 Models by Type")

    stats = service.statistics()

    if stats.get("types"):

        df = pd.DataFrame(stats["types"])

        st.dataframe(
            df,
            hide_index=True,
            use_container_width=True
        )

    ###########################################################
    # Footer
    ###########################################################

    service.close()

    st.divider()

    st.caption(
        "DGX AI Movie Studio • Enterprise Model Manager"
    )


if __name__ == "__main__":

    run()
