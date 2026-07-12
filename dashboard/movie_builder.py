"""
Movie Builder
DGX AI Movie Studio

Phases B + E UI: pick a story whose scenes have images, optionally add spoken
narration, render an MP4, then play and download it. Thin UI over MovieService.
"""

import streamlit as st

from services.movie_service import MovieService


def run():
    st.title("🎥 Movie Builder")
    st.caption("Scene Images (+ Narration) → MP4 Movie")

    service = MovieService()

    if not service.ffmpeg_available():
        st.error(
            "ffmpeg is not installed, so movies can't be rendered yet.\n\n"
            "Install it with:  sudo apt install -y ffmpeg"
        )
        return

    stories = service.stories.list_all()
    if not stories:
        st.info("No stories yet. Create one in the Storyboard page first.")
        return

    labels = {
        f"#{s['id']} — {s['title']} ({s['status']})": s["id"]
        for s in stories
    }
    chosen_label = st.selectbox("Select a story", list(labels.keys()))
    story_id = labels[chosen_label]

    scenes = service.scenes_with_images(story_id)
    total = len(service.scenes.list_by_story(story_id))
    st.write(f"Scenes with images: **{len(scenes)} / {total}**")

    if not scenes:
        st.warning(
            "This story has no scene images yet. Go to the Storyboard page and "
            "use 'Generate Images for All Scenes' first."
        )
        return

    # ----------------------------------------------------------------
    # Options
    # ----------------------------------------------------------------
    col1, col2 = st.columns(2)
    with col1:
        seconds = st.slider(
            "Minimum seconds per scene", min_value=1.0, max_value=10.0,
            value=3.0, step=0.5,
        )
    with col2:
        fade = st.checkbox("Fade between scenes", value=True)

    narration_problem = service.narration.status_message()

    if narration_problem:
        st.info(
            "Narration is unavailable (movies will be silent):\n\n"
            f"{narration_problem}"
        )
        narrate = False
    else:
        done = service.narration.narration_count(story_id)
        narrate = st.checkbox(
            "🎙 Add spoken narration (Piper TTS)", value=True
        )
        if narrate:
            st.caption(
                f"Narration already generated for {done}/{total} scenes. "
                "Missing scenes will be voiced during the build. With "
                "narration on, each scene stays on screen for at least as "
                "long as its voiceover."
            )

    if not narrate:
        est = len(scenes) * seconds
        st.caption(f"Estimated length: ~{est:.0f} seconds")

    # ----------------------------------------------------------------
    # Build
    # ----------------------------------------------------------------
    if st.button("🎬 Build Movie", type="primary"):
        try:
            spinner_text = (
                "Generating narration and rendering movie..."
                if narrate else
                "Rendering movie with ffmpeg..."
            )
            with st.spinner(spinner_text):
                service.build_movie(
                    story_id,
                    seconds_per_scene=seconds,
                    fade=fade,
                    narrate=narrate,
                )
            st.success("Movie built successfully.")
        except Exception as exc:
            st.error(f"Movie build failed:\n\n{exc}")
            return

    # Show the current movie (freshly built or from a previous run).
    movie = service.movie_path(story_id)
    if movie:
        st.divider()
        st.subheader("Preview")
        st.video(movie)
        with open(movie, "rb") as f:
            st.download_button(
                "⬇ Download MP4",
                data=f.read(),
                file_name=f"story_{story_id}.mp4",
                mime="video/mp4",
            )
