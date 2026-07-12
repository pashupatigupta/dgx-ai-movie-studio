"""
Movie Builder
DGX AI Movie Studio

Phases B + E UI: pick a story whose scenes have images, optionally add spoken
narration (choosing a voice), render an MP4, then play and download it.
"""

import streamlit as st

from services.movie_service import MovieService
from services.narration_service import (
    NarrationService, available_voices, DEFAULT_VOICE,
)


def run():
    st.title("🎥 Movie Builder")
    st.caption("Scene Images (+ Narration) → MP4 Movie")

    if not MovieService.ffmpeg_available():
        st.error(
            "ffmpeg is not installed, so movies can't be rendered yet.\n\n"
            "Install it with:  sudo apt install -y ffmpeg"
        )
        return

    # ---- voice selection (before building the service) --------------
    voices = available_voices()
    voice = DEFAULT_VOICE
    if voices:
        default_index = (
            voices.index(DEFAULT_VOICE) if DEFAULT_VOICE in voices else 0
        )
        voice = st.selectbox("🎙 Narrator voice", voices, index=default_index)

    service = MovieService(voice=voice)

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
            "This story has no scene images yet. Go to the Storyboard page "
            "and use 'Generate Images for All Scenes' first."
        )
        return

    # ---- options ----------------------------------------------------
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
        narrate = st.checkbox(
            "🎙 Add spoken narration (Piper TTS)", value=True
        )
        if narrate:
            done = service.narration.narration_count(story_id)
            st.caption(
                f"Narration cached for {done}/{total} scenes with this voice. "
                "Scenes stay on screen at least as long as their voiceover."
            )
            if st.button("🔄 Regenerate narration (after editing lines)"):
                removed = service.narration.clear_narration(story_id)
                st.success(
                    f"Cleared {removed} cached narration file(s). "
                    "They'll be re-voiced on the next build."
                )

    if not narrate:
        st.caption(f"Estimated length: ~{len(scenes) * seconds:.0f} seconds")

    # ---- build ------------------------------------------------------
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
