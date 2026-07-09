"""
Model Configuration
DGX AI Movie Studio
"""

IMAGE_MODELS = {

    "SDXL Base": {
        "workflow": "workflows/sdxl_base.json",
        "type": "image"
    },

    "SDXL Refiner": {
        "workflow": "workflows/sdxl_refiner.json",
        "type": "image"
    },

    "FLUX Schnell": {
        "workflow": "workflows/flux_schnell.json",
        "type": "image"
    },

    "FLUX Dev": {
        "workflow": "workflows/flux_dev.json",
        "type": "image"
    }

}

VIDEO_MODELS = {

    "Stable Video Diffusion": {
        "workflow": "workflows/stable_video.json",
        "type": "video"
    },

    "Wan 2.2": {
        "workflow": "workflows/wan22.json",
        "type": "video"
    },

    "Hunyuan Video": {
        "workflow": "workflows/hunyuan_video.json",
        "type": "video"
    }

}
