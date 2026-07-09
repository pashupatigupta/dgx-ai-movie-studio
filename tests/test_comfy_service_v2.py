from services.comfy_service import (
    queue_prompt,
    wait_for_completion,
    get_images,
)

from services.workflow_builder import WorkflowBuilder


builder = WorkflowBuilder()

builder.set_prompt(
    "Ultra realistic NVIDIA DGX Spark AI Factory"
)

builder.set_negative_prompt(
    "blurry"
)

builder.set_filename(
    "DGX_V2"
)

workflow = builder.build()

response = queue_prompt(workflow)

prompt_id = response["prompt_id"]

print("Prompt ID:", prompt_id)

history = wait_for_completion(prompt_id)

print("Completed")

images = get_images(history)

print(images)
