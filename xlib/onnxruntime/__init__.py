# onnxruntime-gpu >= 1.21 ships CUDA/cuDNN from pip packages (nvidia-*).
# Preload them so CUDAExecutionProvider can find cublasLt/cudnn DLLs without
# a system-wide CUDA Toolkit. Needed for RTX 50xx (Blackwell, sm_120) setups.
try:
    import onnxruntime as _rt
    if hasattr(_rt, 'preload_dlls') and 'CUDAExecutionProvider' in _rt.get_available_providers():
        _rt.preload_dlls()
except Exception as e:
    print(f'onnxruntime preload_dlls error: {e}')

from .device import (ORTDeviceInfo, get_available_devices_info,
                     get_cpu_device_info)
from .InferenceSession import InferenceSession_with_device
