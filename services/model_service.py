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

        self.supported_folders = {
            "checkpoints": "Checkpoint",
            "loras": "LoRA",
            "vae": "VAE",
            "controlnet": "ControlNet",
            "clip": "Text Encoder",
            "embeddings": "Embedding",
            "upscale_models": "Upscaler",
        }

        self.extensions = (
            ".safetensors",
            ".ckpt",
            ".pt",
            ".pth",
            ".bin",
            ".gguf",
        )

    ############################################################

    def classify(self, filename):

        name = filename.lower()

        family = "Unknown"
        vendor = "Unknown"
        purpose = "Unknown"
        framework = "Unknown"
        version = ""
        recommended = 1

        ######################################################
        # SDXL
        ######################################################

        if name.startswith("sd_xl"):

            family = "SDXL"
            vendor = "Stability AI"
            purpose = "Image Generation"
            framework = "Stable Diffusion XL"

            if "refiner" in name:
                version = "Refiner 1.0"
            elif "0.9vae" in name:
                version = "0.9 VAE"
            else:
                version = "1.0"

        ######################################################
        # FLUX
        ######################################################

        elif name.startswith("flux"):

            family = "FLUX"
            vendor = "Black Forest Labs"
            purpose = "Image Generation"
            framework = "FLUX"

            if "dev" in name:
                version = "Dev"
            elif "schnell" in name:
                version = "Schnell"

        ######################################################
        # WAN
        ######################################################

        elif name.startswith("wan"):

            family = "WAN"
            vendor = "Alibaba"
            purpose = "Video Generation"
            framework = "WAN"

        ######################################################
        # Hunyuan
        ######################################################

        elif "hunyuan" in name:

            family = "Hunyuan"
            vendor = "Tencent"
            purpose = "Video Generation"
            framework = "Hunyuan"

        ######################################################
        # Stable Video
        ######################################################

        elif "stable_video" in name or "svd" in name:

            family = "Stable Video"
            vendor = "Stability AI"
            purpose = "Video Generation"
            framework = "Stable Video Diffusion"

        ######################################################
        # GGUF
        ######################################################

        elif filename.endswith(".gguf"):

            family = "LLM"
            vendor = "Various"
            purpose = "Text Generation"
            framework = "GGUF"

        return {
            "family": family,
            "vendor": vendor,
            "purpose": purpose,
            "framework": framework,
            "version": version,
            "recommended": recommended,
            "discovered_by": "Enterprise Scanner",
        }

    ############################################################

    def scan(self):

        models = []

        for folder, model_type in self.supported_folders.items():

            directory = self.models_root / folder

            if not directory.exists():
                continue

            for file in directory.rglob("*"):

                if not file.is_file():
                    continue

                if file.suffix.lower() not in self.extensions:
                    continue

                ##################################################
                # Ignore internal HuggingFace/Diffusers artifacts
                ##################################################

                if file.name.startswith("diffusion_pytorch_model"):
                    continue

                if file.name.startswith("openvino_model"):
                    continue

                if file.name in (
                    "model.safetensors",
                    "model.fp16.safetensors",
                ):
                    continue

                ##################################################

                metadata = self.classify(file.name)

                models.append({

                    "name": file.name,

                    "type": model_type,

                    "folder": folder,

                    "path": str(file),

                    "size": round(
                        file.stat().st_size / 1024 / 1024,
                        2
                    ),

                    "family": metadata["family"],

                    "vendor": metadata["vendor"],

                    "purpose": metadata["purpose"],

                    "framework": metadata["framework"],

                    "version": metadata["version"],

                    "recommended": metadata["recommended"],

                    "discovered_by": metadata["discovered_by"]

                })

        models.sort(

            key=lambda x: (
                x["family"],
                x["type"],
                x["name"]
            )

        )

        return models
