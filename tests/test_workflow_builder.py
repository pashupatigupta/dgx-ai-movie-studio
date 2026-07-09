from services.workflow_builder import WorkflowBuilder

builder = WorkflowBuilder()

builder.set_prompt(
    "NVIDIA DGX Spark inside a futuristic AI factory"
)

builder.set_negative_prompt(
    "blurry, low quality"
)

builder.set_resolution(1024,1024)

builder.set_seed(12345)

builder.set_steps(30)

builder.set_cfg(8)

builder.set_checkpoint(
    "sd_xl_base_1.0.safetensors"
)

builder.set_filename(
    "DGX_TEST"
)

workflow = builder.build()

print(workflow["7"]["inputs"]["text"])

print(workflow["4"]["inputs"])

print(workflow["5"]["inputs"])

print(workflow["8"]["inputs"])

print(workflow["6"]["inputs"])
