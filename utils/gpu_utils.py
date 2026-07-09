import subprocess

import torch

from pynvml import *

try:

    nvmlInit()

    HANDLE = nvmlDeviceGetHandleByIndex(0)

except:

    HANDLE = None


def get_gpu_info():

    gpu = {}

    gpu["cuda"] = torch.cuda.is_available()

    gpu["cuda_version"] = torch.version.cuda

    gpu["gpu_count"] = torch.cuda.device_count()

    if torch.cuda.is_available():

        gpu["gpu_name"] = torch.cuda.get_device_name(0)

    else:

        gpu["gpu_name"] = "No GPU"

    try:

        result = subprocess.check_output(
            ["nvidia-smi"]
        ).decode()

        gpu["driver"] = result.split(
            "Driver Version:"
        )[1].split(
            "CUDA"
        )[0].strip()

    except:

        gpu["driver"] = "Unknown"

    if HANDLE:

        try:

            gpu["temperature"] = nvmlDeviceGetTemperature(
                HANDLE,
                NVML_TEMPERATURE_GPU
            )

        except:

            gpu["temperature"] = "N/A"

        try:

            gpu["power"] = round(
                nvmlDeviceGetPowerUsage(HANDLE)/1000,
                2
            )

        except:

            gpu["power"] = "N/A"

        try:

            util = nvmlDeviceGetUtilizationRates(HANDLE)

            gpu["gpu_util"] = util.gpu

            gpu["memory_util"] = util.memory

        except:

            gpu["gpu_util"] = "N/A"

            gpu["memory_util"] = "N/A"

        gpu["allocated"] = round(
            torch.cuda.memory_allocated()/1024**3,
            2
        )

        gpu["reserved"] = round(
            torch.cuda.memory_reserved()/1024**3,
            2
        )

    return gpu