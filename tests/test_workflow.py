from services.comfy_service import load_workflow

workflow = load_workflow("workflows/sdxl_base.json")

print(type(workflow))

print("Number of Nodes:", len(workflow))

print("\nNode IDs:")

for node in workflow.keys():
    print(node)
