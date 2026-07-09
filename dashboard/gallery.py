import streamlit as st

from services.gallery_service import GalleryService

gallery = GalleryService()


def run():

    st.title("🖼 Image Gallery")

    images = gallery.get_images()

    if len(images) == 0:

        st.info("No images generated yet.")

        return

    cols = st.columns(3)

    for i, image in enumerate(images):

        with cols[i % 3]:

            st.image(
                image["path"],
                use_container_width=True
            )

            st.write(image["filename"])

            st.caption(
                f'{image["size_mb"]} MB'
            )
