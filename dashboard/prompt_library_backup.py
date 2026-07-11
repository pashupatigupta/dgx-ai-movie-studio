from core.session import load_prompt
import streamlit as st

from services.prompt_service import PromptService


def run():

    st.title("📝 Enterprise Prompt Library")

    service = PromptService()

    stats = service.get_statistics()

    st.markdown("---")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Prompts", stats["total"])

    c2.metric("Categories", stats["categories"])

    c3.metric("Favorites", stats["favorites"])

    c4.metric("Total Used", stats["used"])

    st.markdown("---")

    left, right = st.columns([3, 1])

    search = left.text_input(
        "Search Prompt",
        placeholder="Search by title, category or prompt..."
    )

    categories = ["All"] + service.get_categories()

    category = right.selectbox(
        "Category",
        categories
    )

    st.markdown("---")

    if search:

        prompts = service.search(search)

    elif category != "All":

        prompts = service.get_by_category(category)

    else:

        prompts = service.list_prompts()

    if len(prompts) == 0:

        st.info("No prompts found.")

        return

    for row in prompts:

        with st.container():

            st.subheader(row["title"])

            col1, col2 = st.columns([5, 1])

            with col1:

                st.write("**Category:**", row["category"])

                st.write("**Prompt**")

                st.code(row["prompt"])

                st.write("**Negative Prompt**")

                st.code(row["negative_prompt"])

                st.write(
                    f"Model: {row['model']} | "
                    f"{row['width']}x{row['height']} | "
                    f"Steps: {row['steps']} | "
                    f"CFG: {row['cfg']}"
                )

                st.caption(
                    f"Used {row['use_count']} times"
                )

            with col2:

                if row["favorite"]:

                    if st.button(
                        "💔",
                        key=f"fav{row['id']}"
                    ):

                        service.unfavorite(row["id"])

                        st.rerun()

                else:

                    if st.button(
                        "❤️",
                        key=f"unfav{row['id']}"
                    ):

                        service.favorite(row["id"])

                        st.rerun()


if st.button(

    "🚀 Use Prompt",

    key=f"use_{row['id']}"

):

    load_prompt(row)

    service.update_usage(row["id"])

    st.success(

        "Prompt loaded into Image Studio"

    )
                if st.button(
                    "🗑",
                    key=f"delete{row['id']}"
                ):

                    service.delete_prompt(row["id"])

                    st.rerun()

            st.markdown("---")

    st.sidebar.markdown("## 📊 Quick View")

    st.sidebar.write("### ⭐ Favorites")

    favorites = service.get_favorites()

    for item in favorites:

        st.sidebar.write("•", item["title"])

    st.sidebar.markdown("---")

    st.sidebar.write("### 🔥 Most Used")

    for item in service.most_used(5):

        st.sidebar.write(

            f"{item['title']} ({item['use_count']})"

        )

    service.close()
