from repositories.model_repository import ModelRepository

repo = ModelRepository()

print()

print("Statistics")

print(repo.statistics())

print()

print("Models")

for model in repo.get_all():

    print(

        model["id"],

        model["name"],

        model["model_type"]

    )

print()

print("Default")

print(

    repo.get_default()

)

repo.close()
