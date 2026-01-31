import matplotlib.pyplot as plt
import numpy as np

# ... inside main(), after results = run_tensor_benchmark(...)

lst_blurred = results["torch_blur"]

# Use same color scale for both images (very important for fair comparison)
vmin = np.nanpercentile(lst_array, 2)
vmax = np.nanpercentile(lst_array, 98)

plt.figure(figsize=(11, 4))

ax1 = plt.subplot(1, 2, 1)
im1 = ax1.imshow(lst_array, cmap="inferno", vmin=vmin, vmax=vmax)
ax1.set_title("Original LST")
ax1.set_axis_off()
plt.colorbar(im1, ax=ax1, fraction=0.046, label="LST (°C)")

ax2 = plt.subplot(1, 2, 2)
im2 = ax2.imshow(lst_blurred, cmap="inferno", vmin=vmin, vmax=vmax)
ax2.set_title("Gaussian-smoothed LST")
ax2.set_axis_off()
plt.colorbar(im2, ax=ax2, fraction=0.046, label="LST (°C)")

plt.suptitle("MODIS LST (2025): Before vs After Gaussian Smoothing", y=1.02)
plt.tight_layout()

# Save
out_path = "Outputs/Maps/Tensor_Gaussian_Blur.png"
plt.savefig(out_path, dpi=300, bbox_inches="tight")
plt.show()

print("Saved:", out_path)
