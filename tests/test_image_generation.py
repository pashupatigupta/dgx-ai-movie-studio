from services.image_generation_service import generate_image

print()

print("="*60)

print("Testing Image Generation")

print("="*60)

result = generate_image(

    model_name="Stable Diffusion",

    prompt="A futuristic AI Data Center",

    negative_prompt="",

    height=512,

    width=512,

    steps=25,

    guidance=7.5,

    seed=123

)

print(result)

print()

print("Image Generated Successfully")