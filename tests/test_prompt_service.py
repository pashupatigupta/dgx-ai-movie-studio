from services.prompt_service import PromptService

service = PromptService()

service.add_prompt(

    title="DGX AI Factory",

    category="AI Factory",

    prompt="Ultra realistic NVIDIA DGX AI Factory",

    negative_prompt="blurry"

)

rows = service.get_prompts()

for row in rows:

    print(row)
