from services.comfy_service import load_workflow

workflow = load_workflow("workflows/sdxl_base.json")

print(type(workflow))
print(workflow)
