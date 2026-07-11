"""
Enterprise Model Discovery Service
DGX AI Movie Studio
"""

from pathlib import Path


class ModelService:

    def __init__(self):

        self.models_root = (
            Path.home()
            / "jupyterlab"
            / "ComfyUI"
            / "models"
        )

        self.supported = {

            "checkpoints": "Checkpoint",

            "loras": "LoRA",

            "vae": "VAE",

            "clip": "Text Encoder",

            "embeddings": "Embedding",

            "controlnet": "ControlNet",

            "upscale_models": "Upscaler"

        }

        self.valid_extensions = (

            ".safetensors",

            ".ckpt",

            ".pt",

            ".pth",

            ".bin"

        )

    ##############################################################

    def scan(self):

        models = []

        for folder, model_type in self.supported.items():

            directory = self.models_root / folder

            if not directory.exists():

                continue

            for file in directory.rglob("*"):

                if not file.is_file():

                    continue

                if file.suffix.lower() not in self.valid_extensions:

                    continue

                ####################################################
                # Ignore HuggingFace / Diffusers internal files
                ####################################################

                if file.name.startswith(
                    "diffusion_pytorch_model"
                ):

                    continue

                if file.name.startswith(
                    "openvino_model"
                ):

                    continue

                if file.name in (

                    "model.safetensors",

                    "model.fp16.safetensors"

                ):

                    continue

                ####################################################

                size = round(

                    file.stat().st_size
                    / 1024
                    / 1024,

                    2

                )

                models.append(

                    {

                        "name": file.name,

                        "type": model_type,

                        "folder": folder,

                        "path": str(file),

                        "size": size

                    }

                )

        ##########################################################

        models.sort(

            key=lambda x: (

                x["type"],

                x["name"]

            )

        )

        return models
