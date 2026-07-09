"""
Enterprise Image Service
"""

import shutil
import time
from pathlib import Path

from services.workflow_builder import WorkflowBuilder
from services.comfy_service import (
    queue_prompt,
    wait_for_completion,
    get_images,
)

PROJECT_OUTPUT = Path("generated/images")
COMFY_OUTPUT = Path.home() / "jupyterlab/ComfyUI/output"


class ImageService:

    def __init__(self):

        PROJECT_OUTPUT.mkdir(
            parents=True,
            exist_ok=True
        )

    def generate_image(
        self,
        prompt,
        negative_prompt,
        width,
        height,
        steps,
        cfg,
        seed,
        checkpoint,
        filename,
    ):

        builder = WorkflowBuilder()

        builder.set_prompt(prompt)
        builder.set_negative_prompt(negative_prompt)
        builder.set_resolution(width, height)
        builder.set_steps(steps)
        builder.set_cfg(cfg)
        builder.set_seed(seed)
        builder.set_checkpoint(checkpoint)
        builder.set_filename(filename)

        workflow = builder.build()

        response = queue_prompt(workflow)

        prompt_id = response["prompt_id"]

        history = wait_for_completion(prompt_id)

        images = get_images(history)

        if not images:
            raise RuntimeError("No image returned from ComfyUI.")

        image = images[0]

        comfy_file = COMFY_OUTPUT / image["filename"]

        project_file = PROJECT_OUTPUT / image["filename"]

        shutil.copy2(comfy_file, project_file)

        return {
            "prompt_id": prompt_id,
            "filename": image["filename"],
            "image": str(project_file),
            "generation_time": time.strftime("%H:%M:%S"),
        }
