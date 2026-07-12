"""
Storyboard
DGX AI Movie Studio

Phase A UI: turn a single text prompt into a multi-scene storyboard, edit each
scene, and generate an image per scene.

Each scene carries TWO texts, edited separately:
    Image prompt   -> what SDXL draws (style tags welcome)
    Narration line -> what the narrator says (plain prose, no style tags)
"""

import streamlit as st

from services.storyboard_service import StoryboardService


def run():
    st.title("🎬 Storyboard Generator")
    st.caption("Text → Storyboard → Scene Images")

    service = StoryboardService()

    tab_create, tab_library = st.tabs(["Create New", "Story Library"])

    # ----------------------------------------------------------------
    # Create new storyboard
    # ----------------------------------------------------------------
    with tab_create:
        st.subheader("New Storyboard")

        title = st.text_input("Story Title", value="Untitled Story")
        prompt = st.text_area(
            "Story Prompt",
            value="A robot discovers humanity",
            height=120,
        )

        col1, col2, col3 = st.columns(3)
        with col1:
            genre = st.text_input("Genre", value="Sci-Fi")
        with col2:
            style = st.text_input("Style", value="cinematic, photorealistic")
        with col3:
            scene_count = st.number_input(
                "Scenes", min_value=1, max_value=20, value=5, step=1
            )

        if st.button("Generate Storyboard", type="primary"):
            if not prompt.strip():
                st.warning("Please enter a story prompt.")
            else:
                story_id = service.create_storyboard(
                    title=title,
                    prompt=prompt,
                    genre=genre,
                    style=style,
                    scene_count=int(scene_count),
                )
                st.session_state["active_story_id"] = story_id
                st.success(
                    f"Storyboard created (story #{story_id}). "
                    "Open the 'Story Library' tab to edit and render it."
                )

    # ----------------------------------------------------------------
    # Story library
    # ----------------------------------------------------------------
    with tab_library:
        st.subheader("Story Library")

        stories = service.list_stories()
        if not stories:
            st.info("No stories yet. Create one in the 'Create New' tab.")
            return

        labels = {
            f"#{s['id']} — {s['title']} ({s['status']})": s["id"]
            for s in stories
        }

        id_list = list(labels.values())
        active_id = st.session_state.get("active_story_id")
        default_index = id_list.index(active_id) if active_id in id_list else 0

        chosen_label = st.selectbox(
            "Select a story",
            list(labels.keys()),
            index=default_index,
        )
        story_id = labels[chosen_label]
        story = service.get_story(story_id)

        st.write(f"**Prompt:** {story['prompt']}")
        st.write(
            f"**Genre:** {story['genre']}  |  "
            f"**Style:** {story['style']}  |  "
            f"**Status:** {story['status']}"
        )

        if st.button("🎨 Generate Images for All Scenes"):
            with st.spinner(
                "Generating scene images on the DGX GPU — this can take a "
                "while for many scenes..."
            ):
                service.generate_all_images(story_id)
            st.success("All scene images generated.")

        st.caption(
            "Tip: the **image prompt** is what SDXL draws (style tags are "
            "fine). The **narration line** is what the narrator speaks — keep "
            "it plain prose, no style tags."
        )
        st.divider()

        for scene in service.get_scenes(story_id):
            st.markdown(f"### {scene['title']}")

            new_desc = st.text_area(
                "🖼 Image prompt",
                value=scene["description"] or "",
                key=f"desc_{scene['id']}",
                height=90,
            )

            new_narration = st.text_area(
                "🎙 Narration line (spoken)",
                value=scene.get("narration_text") or "",
                key=f"narr_{scene['id']}",
                height=70,
            )

            c1, c2 = st.columns(2)
            with c1:
                if st.button("Save", key=f"save_{scene['id']}"):
                    service.update_scene(
                        scene_id=scene["id"],
                        title=scene["title"],
                        description=new_desc,
                        narration_text=new_narration,
                    )
                    st.success(
                        "Saved. (If you changed the narration, use "
                        "'Regenerate narration' in Movie Builder.)"
                    )
            with c2:
                if st.button("Generate Image", key=f"img_{scene['id']}"):
                    scene_for_image = dict(scene)
                    scene_for_image["description"] = new_desc
                    with st.spinner("Generating scene image..."):
                        path = service.generate_scene_image(scene_for_image)
                    st.image(path, caption=scene["title"])

            if scene.get("image_path"):
                st.image(
                    scene["image_path"],
                    caption=f"{scene['title']} (saved)",
                )

            st.divider()
