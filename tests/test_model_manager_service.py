from services.model_manager_service import ModelManagerService

service = ModelManagerService()

print()

print("Refreshing Models...")

count = service.refresh_models()

print("Indexed:", count)

print()

print("Statistics")

print(service.statistics())

print()

print("All Models")

for model in service.get_models():

    print(

        model["id"],

        model["name"],

        model["model_type"]

    )

print()

print("Default Model")

print(service.get_default_model())

service.close()
