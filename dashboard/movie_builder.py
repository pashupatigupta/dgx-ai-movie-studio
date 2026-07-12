"""
Movie Builder
DGX AI Movie Studio

Phases B + E + F UI: take a story's scene images, optionally add spoken
narration and a music bed, render an MP4, then play and download it.
"""

import streamlit as st

from services.movie_service import MovieService
from services.narration_service import (
    NarrationService, available_voices, DEFAULT_VOICE,
)
from services.music_service import available_tracks, MUSIC_DIR


def run():
    st.title("🎥 Movie Builder")
    st.caption("Scene Images (+ Narration + Music) → MP4 Movie")

    if not MovieService.ffmpeg_available():
        st.error(
            "ffmpeg is not installed, so movies can't be rendered yet.\n\n"
            "Install it with:  sudo apt install -y ffmpeg"
        )
        return

    # ---- narrator voice (chosen before building the service) --------
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

    # ---- timing -----------------------------------------------------
    col1, col2 = st.columns(2)
    with col1:
        seconds = st.slider(
            "Minimum seconds per scene", min_value=1.0, max_value=10.0,
            value=3.0, step=0.5,
        )
    with col2:
        fade = st.checkbox("Fade between scenes", value=True)

    # ---- camera motion ----------------------------------------------
    st.markdown("##### 🎥 Camera motion")

    mcol1, mcol2 = st.columns(2)
    with mcol1:
        motion = st.selectbox(
            "Motion style",
            ["auto", "zoom_in", "zoom_out", "pan_right", "pan_left", "none"],
            index=0,
            help=(
                "A slow push-in or drift across a still image reads as "
                "cinematic. 'auto' varies the movement scene to scene."
            ),
        )
    with mcol2:
        fill = st.checkbox(
            "Fill the frame (crop)", value=True,
            help=(
                "Crops each image to fill 16:9 — no black bars, and room for "
                "the camera to move. Uncheck to letterbox the whole image."
            ),
        )

    # ---- narration --------------------------------------------------
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

    # ---- music ------------------------------------------------------
    st.markdown("##### 🎵 Background music")

    tracks = available_tracks()
    music_track = None
    music_volume = 0.25
    duck_music = True

    if not tracks:
        st.info(
            f"No music tracks yet. Drop .mp3 or .wav files into `{MUSIC_DIR}/` "
            "and they'll show up here.\n\n"
            "Free sources: incompetech.com, freepd.com, or the YouTube Audio "
            "Library."
        )
    else:
        choice = st.selectbox("Track", ["(none)"] + tracks)
        if choice != "(none)":
            music_track = choice
            mcol1, mcol2 = st.columns(2)
            with mcol1:
                music_volume = st.slider(
                    "Music volume", min_value=0.05, max_value=1.0,
                    value=0.25, step=0.05,
                )
            with mcol2:
                duck_music = st.checkbox(
                    "Duck under narration", value=True,
                    help=(
                        "Automatically lowers the music whenever the narrator "
                        "speaks, then brings it back up in the gaps."
                    ),
                )

    if not narrate and not music_track:
        st.caption(f"Estimated length: ~{len(scenes) * seconds:.0f} seconds")

    # ---- build ------------------------------------------------------
    if st.button("🎬 Build Movie", type="primary"):
        try:
            steps = []
            if narrate:
                steps.append("narration")
            if music_track:
                steps.append("music")
            spinner_text = (
                f"Rendering movie ({' + '.join(steps)})..."
                if steps else "Rendering movie with ffmpeg..."
            )

            with st.spinner(spinner_text):
                service.build_movie(
                    story_id,
                    seconds_per_scene=seconds,
                    fade=fade,
                    motion=motion,
                    fill=fill,
                    narrate=narrate,
                    music_track=music_track,
                    music_volume=music_volume,
                    duck_music=duck_music,
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
