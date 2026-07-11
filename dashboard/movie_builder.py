"""
Movie Builder
DGX AI Movie Studio

Phase B UI: pick a story whose scenes have images, render them into an MP4
slideshow, then play and download the result. Thin UI over MovieService.
"""

import streamlit as st

from services.movie_service import MovieService


def run():
    st.title("🎥 Movie Builder")
    st.caption("Scene Images → MP4 Movie")

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

    col1, col2 = st.columns(2)
    with col1:
        seconds = st.slider(
            "Seconds per scene", min_value=1.0, max_value=10.0,
            value=3.0, step=0.5,
        )
    with col2:
        fade = st.checkbox("Fade between scenes", value=True)

    est = len(scenes) * seconds
    st.caption(f"Estimated length: ~{est:.0f} seconds")

    if st.button("🎬 Build Movie", type="primary"):
        with st.spinner("Rendering movie with ffmpeg..."):
            output = service.build_movie(
                story_id,
                seconds_per_scene=seconds,
                fade=fade,
            )
        st.success("Movie built successfully.")

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
