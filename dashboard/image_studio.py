import streamlit as st

from services.image_service import ImageService

service = ImageService()


def run():

    st.title("🖼 DGX AI Image Studio")

    prompt = st.text_area(
        "Prompt",
        value="A futuristic NVIDIA DGX AI Factory"
    )

    negative_prompt = st.text_area(
        "Negative Prompt",
        value="blurry, low quality"
    )

    col1, col2 = st.columns(2)

    with col1:

        width = st.number_input(
            "Width",
            value=1024
        )

        height = st.number_input(
            "Height",
            value=1024
        )

        steps = st.slider(
            "Steps",
            10,
            50,
            30
        )

    with col2:

        cfg = st.slider(
            "CFG",
            1.0,
            15.0,
            8.0
        )

        seed = st.number_input(
            "Seed",
            value=12345
        )

        checkpoint = st.text_input(
            "Checkpoint",
            value="sd_xl_base_1.0.safetensors"
        )

    if st.button("Generate Image"):

        with st.spinner("Generating image..."):

            result = service.generate_image(

                prompt=prompt,

                negative_prompt=negative_prompt,

                width=width,

                height=height,

                steps=steps,

                cfg=cfg,

                seed=seed,

                checkpoint=checkpoint,

                filename="DGX_STREAMLIT"

            )

        st.success("Image Generated Successfully")

        st.image(result["image"])

        st.json(result)

