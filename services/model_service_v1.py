"""
Enterprise Model Service
DGX AI Movie Studio
"""

from pathlib import Path


COMFY_MODELS = Path.home() / "jupyterlab/ComfyUI/models"


MODEL_FOLDERS = {

    "Checkpoint": "checkpoints",

    "LoRA": "loras",

    "VAE": "vae",

    "Embedding": "embeddings",

    "ControlNet": "controlnet",

    "Text Encoder": "text_encoders",

    "UNet": "unet"

}


class ModelService:

    def __init__(self):

        self.root = COMFY_MODELS

    ##################################################

    def scan(self):

        models = []

        for model_type, folder in MODEL_FOLDERS.items():

            path = self.root / folder

            if not path.exists():

                continue

            for file in path.rglob("*"):

                if file.is_file():

                    if file.suffix.lower() not in [

                        ".safetensors",

                        ".ckpt",

                        ".pt",

                        ".bin",

                        ".gguf"

                    ]:

                        continue

                    models.append(

                        {

                            "name": file.name,

                            "type": model_type,

                            "folder": folder,

                            "path": str(file),

                            "size":

                            round(

                                file.stat().st_size

                                /1024/1024,

                                2

                            )

                        }

                    )

        models.sort(

            key=lambda x:

            (

                x["type"],

                x["name"]

            )

        )

        return models

    ##################################################

    def summary(self):

        models = self.scan()

        summary = {}

        for m in models:

            summary[m["type"]] = (

                summary.get(

                    m["type"],

                    0

                ) + 1

            )

        return summary
