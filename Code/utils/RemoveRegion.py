import numpy as np
from skimage.segmentation import find_boundaries


def remove_region(label_img, target_label):
    """Remove labels touching the outer boundary of a selected label.

    This helper records a manual cleanup operation from the napari workflow:
    after selecting a problematic region, neighboring labels that touch its
    boundary can be zeroed out together.
    """
    target_mask = label_img == target_label

    boundary = find_boundaries(target_mask, mode='outer')

    touching_labels = np.unique(label_img[boundary])
    touching_labels = touching_labels[(touching_labels != 0) & (touching_labels != target_label)]

    cleaned = label_img.copy()
    for lbl in touching_labels:
        cleaned[cleaned == lbl] = 0

    return cleaned
