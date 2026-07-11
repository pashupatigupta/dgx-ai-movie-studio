import streamlit as st

from services.prompt_service import PromptService

service = PromptService()


def run():

    st.title("📝 Prompt Library")

    st.subheader("Add Prompt")

    title = st.text_input("Title")

    category = st.text_input("Category")

    prompt = st.text_area("Prompt")

    negative = st.text_area("Negative Prompt")

    if st.button("Save Prompt"):

        service.add_prompt(

            title,

            category,

            prompt,

            negative

        )

        st.success("Prompt Saved")

    st.divider()

    st.subheader("Saved Prompts")

    rows = service.get_prompts()

    for row in rows:

        st.markdown(f"### {row[1]}")

        st.write("Category:", row[2])

        st.write(row[3])

        st.caption(row[4])

        st.divider()
