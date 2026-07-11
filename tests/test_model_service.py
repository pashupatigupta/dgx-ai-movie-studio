from services.model_service import ModelService

service = ModelService()

models = service.scan()

print()

print("Models Found:", len(models))

print()

for model in models:

    print("-" * 60)

    print("Name        :", model["name"])
    print("Type        :", model["type"])
    print("Family      :", model["family"])
    print("Purpose     :", model["purpose"])
    print("Vendor      :", model["vendor"])
    print("Framework   :", model["framework"])
    print("Version     :", model["version"])
