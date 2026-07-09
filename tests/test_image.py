from services.image_service import classify_image, get_gpu_usage
import os

print("=" * 60)
print("DGX AI Movie Studio - Image Classification Test")
print("=" * 60)

IMAGE_PATH = "uploads/test.jpg"

if not os.path.exists(IMAGE_PATH):
    print(f"Image not found: {IMAGE_PATH}")
    print("Copy any JPG image into uploads/test.jpg")
    exit()

result = classify_image(IMAGE_PATH)

print("\nPrediction")
print("------------------------")
print(result["prediction"])

print("\nConfidence")
print("------------------------")
print(f"{result['confidence']} %")

print("\nInference Time")
print("------------------------")
print(f"{result['inference_time']} sec")

print("\nGPU Memory")
print("------------------------")
print(f"{get_gpu_usage()} GB")

print("\nImage Classification Successful")