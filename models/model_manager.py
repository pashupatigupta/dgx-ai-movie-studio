"""
=========================================================
DGX AI Movie Studio
Model Manager
=========================================================
"""

import torch

from diffusers import StableDiffusionPipeline

from utils.logger import logger

# ---------------------------------------------------------
# Loaded Models Cache
# ---------------------------------------------------------

PIPELINES = {}

# ---------------------------------------------------------
# Available Models
# ---------------------------------------------------------

IMAGE_MODELS = {

    "Stable Diffusion":

        "runwayml/stable-diffusion-v1-5",

    "Stable Diffusion XL":

        "stabilityai/stable-diffusion-xl-base-1.0"

}

# ---------------------------------------------------------
# Device
# ---------------------------------------------------------

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

DTYPE = torch.float16 if DEVICE == "cuda" else torch.float32

# ---------------------------------------------------------
# Load Image Model
# ---------------------------------------------------------

def load_image_model(model_name):

    if model_name not in IMAGE_MODELS:

        raise ValueError(

            f"Unknown Model : {model_name}"

        )

    if model_name not in PIPELINES:

        logger.info(

            f"Loading Model : {model_name}"

        )

        model_path = IMAGE_MODELS[model_name]

        pipe = StableDiffusionPipeline.from_pretrained(

            model_path,

            torch_dtype=DTYPE,

            use_safetensors=True

        )

        pipe.to(DEVICE)

        pipe.enable_attention_slicing()

        PIPELINES[model_name] = pipe

        logger.info(

            f"{model_name} Loaded Successfully"

        )

    return PIPELINES[model_name]

# ---------------------------------------------------------
# List Available Models
# ---------------------------------------------------------

def available_models():

    return list(

        IMAGE_MODELS.keys()

    )