from services.image_service import ImageService

service = ImageService()

result = service.generate_image(

    prompt="Ultra realistic NVIDIA DGX Spark AI Factory",

    negative_prompt="blurry",

    width=1024,

    height=1024,

    steps=30,

    cfg=8,

    seed=12345,

    checkpoint="sd_xl_base_1.0.safetensors",

    filename="DGX_MOVIE"

)

print(result)
