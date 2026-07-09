
from utils.gpu_utils import get_gpu_info
gpu = get_gpu_info()

st.metric(
    "GPU Utilization",
    gpu["gpu_utilization"]
)