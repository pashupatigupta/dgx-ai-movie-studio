from services.workflow_builder import WorkflowBuilder

from services.comfy_service import (

    queue_prompt,

    wait_for_completion

)

builder = WorkflowBuilder()

builder.set_prompt(

    "NVIDIA DGX Spark AI Factory"

)

builder.set_negative_prompt(

    "blurry"

)

builder.set_resolution(

    1024,

    1024

)

builder.set_seed(

    12345

)

builder.set_steps(

    30

)

builder.set_cfg(

    8

)

builder.set_filename(

    "DGX_TEST"

)

workflow = builder.build()

response = queue_prompt(workflow)

prompt_id = response["prompt_id"]

print("Prompt ID:", prompt_id)

history = wait_for_completion(prompt_id)

print(history)
