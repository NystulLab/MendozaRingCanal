import numpy as np
from skimage.segmentation import watershed
from skimage.measure import label
from skimage.morphology import ball, erosion
from collections import defaultdict

def SplitLabelsPoints(label_img, points_layer, erosion_radius=0):
    points = np.round(points_layer.data).astype(int)

    label_to_points = defaultdict(list)
    for pt in points:
        pt = tuple(pt)
        if np.all((0 <= pt[i] < label_img.shape[i]) for i in range(label_img.ndim)):
            lbl = label_img[pt]
            if lbl > 0:
                label_to_points[lbl].append(pt)

    new_label_img = label_img.copy()
    max_label = new_label_img.max()

    for lbl, pts in label_to_points.items():
        if len(pts) < 2:
            continue  # No need to split

        mask = (label_img == lbl)

        seeds = np.zeros_like(label_img, dtype=np.int32)
        for i, pt in enumerate(pts):
            seeds[tuple(pt)] = i + 1

        # Dilate seed points to ensure they survive erosion
        from skimage.morphology import ball, dilation
        seeds = dilation(seeds, ball(1))

        if erosion_radius > 0:
            mask = erosion(mask, ball(erosion_radius))
            seeds *= mask  # Remove seeds that no longer fall in the eroded mask

        if np.count_nonzero(seeds) < 2:
            print(f"Skipping label {lbl} due to insufficient valid seeds.")
            continue

        split = watershed(image=np.zeros_like(label_img), markers=seeds, mask=mask)

        # Clear original label
        new_label_img[label_img == lbl] = 0

        for region_id in range(1, split.max() + 1):
            max_label += 1
            new_label_img[(split == region_id)] = max_label

    return new_label_img
