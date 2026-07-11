"""
Enterprise Prompt Library
DGX AI Movie Studio
"""

import streamlit as st

from services.prompt_service import PromptService
from core.session import load_prompt


class PromptLibrary:

    def __init__(self):

        self.service = PromptService()

    ############################################################

    def statistics(self):

        stats = self.service.get_statistics()

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Prompts",
            stats["total"]
        )

        c2.metric(
            "Categories",
            stats["categories"]
        )

        c3.metric(
            "Favorites",
            stats["favorites"]
        )

        c4.metric(
            "Used",
            stats["used"]
        )

    ############################################################

    def filters(self):

        left, right = st.columns([3, 1])

        keyword = left.text_input(
            "Search",
            placeholder="Search prompt..."
        )

        categories = ["All"]

        categories.extend(
            self.service.get_categories()
        )

        category = right.selectbox(
            "Category",
            categories
        )

        return keyword, category

    ############################################################

    def get_prompts(
        self,
        keyword,
        category
    ):

        if keyword:

            return self.service.search(
                keyword
            )

        if category != "All":

            return self.service.get_by_category(
                category
            )

        return self.service.list_prompts()

    ############################################################

    def render(self):

        st.title("📝 Enterprise Prompt Library")

        self.statistics()

        st.divider()

        keyword, category = self.filters()

        st.divider()

        prompts = self.get_prompts(
            keyword,
            category
        )

        if len(prompts) == 0:

            st.info(
                "No prompts found."
            )

            return
        ########################################################

        for row in prompts:

            with st.container():

                st.subheader(row["title"])

                left, right = st.columns([5, 1])

                ################################################

                with left:

                    st.write(
                        "**Category:**",
                        row["category"]
                    )

                    st.write("**Prompt**")

                    st.code(
                        row["prompt"],
                        language=None
                    )

                    st.write(
                        "**Negative Prompt**"
                    )

                    st.code(
                        row["negative_prompt"],
                        language=None
                    )

                    c1, c2, c3, c4 = st.columns(4)

                    c1.metric(
                        "Model",
                        row["model"]
                    )

                    c2.metric(
                        "Resolution",
                        f"{row['width']}×{row['height']}"
                    )

                    c3.metric(
                        "Steps",
                        row["steps"]
                    )

                    c4.metric(
                        "CFG",
                        row["cfg"]
                    )

                    st.caption(

                        f"Seed : {row['seed']}"

                    )

                    st.caption(

                        f"Used : {row['use_count']}"

                    )

                ################################################

                with right:

                    if row["favorite"]:

                        if st.button(

                            "💔",

                            key=f"fav_{row['id']}"

                        ):

                            self.service.unfavorite(

                                row["id"]

                            )

                            st.rerun()

                    else:

                        if st.button(

                            "❤️",

                            key=f"unfav_{row['id']}"

                        ):

                            self.service.favorite(

                                row["id"]

                            )

                            st.rerun()

                    ############################################

                    if st.button(

                        "🚀 Use",

                        key=f"use_{row['id']}"

                    ):

                        load_prompt(row)

                        self.service.update_usage(

                            row["id"]

                        )

                        st.success(

                            "Prompt loaded into Image Studio"

                        )

                    ############################################

                    if st.button(

                        "🗑 Delete",

                        key=f"delete_{row['id']}"

                    ):

                        self.service.delete_prompt(

                            row["id"]

                        )

                        st.rerun()

                st.divider()
    ############################################################
    # Sidebar
    ############################################################

    def sidebar(self):

        st.sidebar.markdown("## ⭐ Favorites")

        favorites = self.service.get_favorites()

        if len(favorites) == 0:

            st.sidebar.info("No favorites")

        else:

            for item in favorites:

                st.sidebar.write(
                    "•",
                    item["title"]
                )

        st.sidebar.divider()

        ########################################################

        st.sidebar.markdown("## 🔥 Most Used")

        most_used = self.service.most_used(5)

        if len(most_used) == 0:

            st.sidebar.info("No prompts")

        else:

            for item in most_used:

                st.sidebar.write(

                    f"{item['title']} "

                    f"({item['use_count']})"

                )

        st.sidebar.divider()

        ########################################################

        st.sidebar.markdown("## 🕒 Recent")

        recent = self.service.recent(5)

        if len(recent) == 0:

            st.sidebar.info("No prompts")

        else:

            for item in recent:

                st.sidebar.write(

                    item["title"]

                )

        st.sidebar.divider()

        ########################################################

        st.sidebar.markdown("## 📤 Export")

        export = self.service.export()

        st.sidebar.download_button(

            label="Download JSON",

            data=str(export),

            file_name="prompt_library.json",

            mime="application/json"

        )

    ############################################################

    def close(self):

        self.service.close()


############################################################
# Streamlit Entry Point
############################################################

def run():

    library = PromptLibrary()

    library.render()

    library.sidebar()

    library.close()
