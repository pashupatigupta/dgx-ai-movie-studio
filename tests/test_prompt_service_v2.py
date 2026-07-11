from services.prompt_service import PromptService

service = PromptService()

rows = service.search_prompt("DGX")

print("Found:", len(rows))

for row in rows:

    print(dict(row))
