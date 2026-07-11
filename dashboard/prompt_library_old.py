import streamlit as st

from services.prompt_service import PromptService

service = PromptService()


def run():

    st.title("📝 Enterprise Prompt Library")

    ####################################################
    # Statistics
    ####################################################

    stats = service.get_statistics()

    c1, c2, c3 = st.columns(3)

    c1.metric("Prompts", stats[0] or 0)

    c2.metric("Favorites", stats[1] or 0)

    c3.metric("Used", stats[2] or 0)

    st.divider()

    ####################################################
    # Search
    ####################################################

    search = st.text_input(
        "🔍 Search Prompt"
    )

    ####################################################
    # Category
    ####################################################

    categories = service.get_categories()

    category = st.selectbox(

        "Category",

        ["All"] + categories

    )

    ####################################################
    # Data
    ####################################################

    if search:

        rows = service.search_prompt(search)

    elif category != "All":

        rows = service.get_by_category(category)

    else:

        rows = service.get_prompts()

    ####################################################
    # Display
    ####################################################

    for row in rows:

        with st.expander(

            f"📄 {row['title']}"

        ):

            st.write(

                "**Category:**",

                row["category"]

            )

            st.write(

                "**Prompt:**"

            )

            st.code(

                row["prompt"]

            )

            st.write(

                "**Negative Prompt:**"

            )

            st.code(

                row["negative_prompt"]

            )

            c1, c2 = st.columns(2)

            if c1.button(

                "⭐ Favorite",

                key=f"fav_{row['id']}"

            ):

                service.favorite(

                    row["id"]

                )

                st.rerun()

            if c2.button(

                "🗑 Delete",

                key=f"del_{row['id']}"

            ):

                service.delete_prompt(

                    row["id"]

                )

                st.rerun()
