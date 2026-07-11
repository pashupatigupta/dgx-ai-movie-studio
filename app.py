import streamlit as st

st.set_page_config(
    page_title="DGX AI Movie Studio",
    page_icon="🎬",
    layout="wide"
)

PAGES = {
    "🏠 Home": "dashboard.home",
    "🖼 Image Studio": "dashboard.image_studio",
    "🎬 Storyboard": "dashboard.storyboard",
    "🖼 Gallery": "dashboard.gallery",
    "📝 Prompt Library": "dashboard.prompt_library",
    "📊 GPU Dashboard": "dashboard.gpu_dashboard",
    "🤖 Model Manager": "dashboard.model_manager",
    "🎥 Movie Builder": "dashboard.movie_builder",
}

st.sidebar.title("DGX AI Movie Studio")

page = st.sidebar.radio(
    "Navigation",
    list(PAGES.keys())
)

module = __import__(
    PAGES[page],
    fromlist=["run"]
)

if hasattr(module, "run"):
    module.run()
