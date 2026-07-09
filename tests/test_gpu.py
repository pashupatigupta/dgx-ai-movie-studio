from utils.gpu_utils import get_gpu_info

gpu = get_gpu_info()

print()

print("="*60)

print("DGX AI Movie Studio")

print("="*60)

for k,v in gpu.items():

    print(f"{k:20} : {v}")