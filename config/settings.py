"""
=========================================================
DGX AI Movie Studio
Global Configuration
=========================================================
"""

from pathlib import Path
import torch

# -------------------------------------------------------
# Project Information
# -------------------------------------------------------

PROJECT_NAME = "DGX AI Movie Studio"

VERSION = "1.0"

AUTHOR = "Pashupati Gupta"

# -------------------------------------------------------
# Base Paths
# -------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

UPLOAD_DIR = BASE_DIR / "uploads"

OUTPUT_DIR = BASE_DIR / "outputs"

CACHE_DIR = BASE_DIR / "cache"

LOG_DIR = BASE_DIR / "logs"

DATABASE_DIR = BASE_DIR / "database"

# -------------------------------------------------------
# Device Configuration
# -------------------------------------------------------

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

DTYPE = torch.float16 if DEVICE == "cuda" else torch.float32

# -------------------------------------------------------
# Default AI Models
# -------------------------------------------------------

DEFAULT_IMAGE_MODEL = "Stable Diffusion"

DEFAULT_LLM = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

DEFAULT_VIDEO_MODEL = "stabilityai/stable-video-diffusion-img2vid"

# -------------------------------------------------------
# Streamlit Configuration
# -------------------------------------------------------

PAGE_TITLE = PROJECT_NAME

PAGE_LAYOUT = "wide"

# -------------------------------------------------------
# Output Directories
# -------------------------------------------------------

IMAGE_OUTPUT_DIR = OUTPUT_DIR / "images"

VIDEO_OUTPUT_DIR = OUTPUT_DIR / "videos"

MOVIE_OUTPUT_DIR = OUTPUT_DIR / "movies"

# -------------------------------------------------------
COMFY_URL = "http://127.0.0.1:8188"

COMFY_PROMPT_API = "/prompt"

COMFY_HISTORY_API = "/history"

COMFY_VIEW_API = "/view"

COMFY_UPLOAD_API = "/upload/image"

# Create Required Directories Automatically
# -------------------------------------------------------

for directory in [

    UPLOAD_DIR,

    OUTPUT_DIR,

    IMAGE_OUTPUT_DIR,

    VIDEO_OUTPUT_DIR,

    MOVIE_OUTPUT_DIR,

    CACHE_DIR,

    LOG_DIR,

    DATABASE_DIR

]:

    directory.mkdir(

        parents=True,

        exist_ok=True

    )
#-------------------------------------------------------------
# ----------------------------
# ComfyUI
# ----------------------------

COMFY_URL = "http://127.0.0.1:8188"