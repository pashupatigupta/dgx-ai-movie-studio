"""
Image Studio
DGX AI Movie Studio

Text -> Image via ComfyUI (SDXL).

This page is intentionally thin: all real work is delegated to the
existing service layer (ImageService -> WorkflowBuilder -> ComfyUI).
The UI only collects parameters and displays the result.
"""

import streamlit as st

from core.session import initialize
from services.image_service import ImageService


def run():
    # Session/state setup (safe to call on every rerun).
    initialize()

    st.title("🖼 DGX AI Image Studio")
    st.caption("Text → Image via ComfyUI (SDXL) on NVIDIA DGX Spark")

    service = ImageService()

    # ----------------------------------------------------------------
    # Prompt inputs
    # ----------------------------------------------------------------
    prompt = st.text_area(
        "Prompt",
        value="A robot discovers humanity, cinematic lighting, highly detailed",
        height=140,
    )

    negative_prompt = st.text_area(
        "Negative Prompt",
        value="blurry, low quality, distorted, watermark, text",
        height=100,
    )

    # ----------------------------------------------------------------
    # Generation parameters
    # ----------------------------------------------------------------
    col1, col2 = st.columns(2)

    with col1:
        width = st.number_input(
            "Width", min_value=256, max_value=2048, value=1024, step=64
        )
        height = st.number_input(
            "Height", min_value=256, max_value=2048, value=1024, step=64
        )
        steps = st.slider("Steps", min_value=5, max_value=80, value=30)

    with col2:
        cfg = st.slider(
            "CFG", min_value=1.0, max_value=20.0, value=8.0, step=0.5
        )
        seed = st.number_input("Seed", min_value=0, value=12345, step=1)
        checkpoint = st.text_input(
            "Checkpoint", value="sd_xl_base_1.0.safetensors"
        )

    # ----------------------------------------------------------------
    # Generate
    # ----------------------------------------------------------------
    if st.button("Generate Image", type="primary"):

        if not prompt.strip():
            st.warning("Please enter a prompt first.")
            return

        try:
            with st.spinner("Generating image on the DGX GPU..."):
                result = service.generate_image(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    width=int(width),
                    height=int(height),
                    steps=int(steps),
                    cfg=float(cfg),
                    seed=int(seed),
                    checkpoint=checkpoint,
                    filename="DGX_STREAMLIT",
                )
        except Exception as exc:
            st.error(f"Image generation failed: {exc}")
            st.info(
                "Common causes:\n"
                "1. ComfyUI is not running on http://127.0.0.1:8188\n"
                "2. The checkpoint name does not exist in "
                "ComfyUI/models/checkpoints\n"
                "3. Node IDs in workflows/sdxl_api.json don't match "
                "services/workflow_builder.py"
            )
            return

        st.success("Image generated successfully.")
        st.image(result["image"], caption=result["filename"])
        st.json(result)
