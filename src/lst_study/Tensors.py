"""
Tensors.py
-----------
Gaussian smoothing of Land Surface Temperature (LST)
and performance comparison: NumPy vs PyTorch
"""

import time
import numpy as np
def gaussian_kernel(size: int = 11, sigma: float = 2.0) -> np.ndarray:
    """
    Create a 2D Gaussian kernel (size x size) normalized to sum to 1.
    size must be an odd number (e.g., 5, 7, 11).
    """
    if size % 2 == 0:
        raise ValueError("size must be odd (e.g., 5, 7, 11)")

    ax = np.arange(-(size // 2), size // 2 + 1, dtype=np.float32)
    xx, yy = np.meshgrid(ax, ax)
    kernel = np.exp(-(xx**2 + yy**2) / (2.0 * sigma**2))
    kernel /= kernel.sum()
    return kernel.astype(np.float32)

def gaussian_blur_numpy(lst_2d: np.ndarray, size: int = 11, sigma: float = 2.0):
    """
    Apply Gaussian blur to a 2D array using NumPy.
    Returns: (blurred_array, runtime_seconds)
    """
    lst = lst_2d.astype(np.float32)
    kernel = gaussian_kernel(size=size, sigma=sigma)
    K = kernel.shape[0]
    pad = K // 2

    # Pad edges so output stays same shape
    padded = np.pad(lst, pad_width=pad, mode="edge")
    out = np.zeros_like(lst, dtype=np.float32)

    t0 = time.perf_counter()
    # simple (clear) convolution loops
    H, W = lst.shape
    for i in range(H):
        for j in range(W):
            window = padded[i:i+K, j:j+K]
            out[i, j] = np.sum(window * kernel)
    dt = time.perf_counter() - t0

    return out, dt
def gaussian_blur_torch(lst_2d: np.ndarray, size: int = 11, sigma: float = 2.0, device: str | None = None):
    """
    Apply Gaussian blur using PyTorch conv2d.
    Returns: (blurred_array, runtime_seconds, device_used)
    """
    import torch
    import torch.nn.functional as F

    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"

    lst = lst_2d.astype(np.float32)

    # kernel: (K,K) -> torch (1,1,K,K)
    kernel = gaussian_kernel(size=size, sigma=sigma)
    k = torch.from_numpy(kernel).to(device).unsqueeze(0).unsqueeze(0)

    # image: (H,W) -> torch (1,1,H,W)
    x = torch.from_numpy(lst).to(device).unsqueeze(0).unsqueeze(0)

    pad = size // 2

    # Warm-up for fair timing (especially important on GPU)
    _ = F.conv2d(F.pad(x, (pad, pad, pad, pad), mode="replicate"), k)
    if device == "cuda":
        torch.cuda.synchronize()

    t0 = time.perf_counter()
    y = F.conv2d(F.pad(x, (pad, pad, pad, pad), mode="replicate"), k)
    if device == "cuda":
        torch.cuda.synchronize()
    dt = time.perf_counter() - t0

    out = y.squeeze().detach().cpu().numpy()
    return out, dt, device

def run_tensor_benchmark(lst_2d: np.ndarray, size: int = 11, sigma: float = 2.0) -> dict:
    """
    Runs Gaussian smoothing with NumPy and PyTorch and returns timings + outputs.
    """
    np_blur, t_np = gaussian_blur_numpy(lst_2d, size=size, sigma=sigma)
    torch_blur, t_torch, device = gaussian_blur_torch(lst_2d, size=size, sigma=sigma)

    return {
        "numpy_time_sec": t_np,
        "torch_time_sec": t_torch,
        "torch_device": device,
        "numpy_blur": np_blur,
        "torch_blur": torch_blur,
        "kernel_size": size,
        "sigma": sigma,
    }
