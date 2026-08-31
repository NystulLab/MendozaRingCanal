import numpy as np
from skimage.morphology import erosion, dilation, ball
from skimage.measure import label


def SplitLabels(label_img, target_labels, erosion_radius=1):
    """Split selected labels into separate 3D connected components.

    The function erodes each selected label, labels the disconnected pieces, and
    dilates those pieces back into the original label mask. It is intended for
    manual cleanup after napari review, where over-merged objects have known
    label IDs.
    """
    max_label = label_img.max()
    new_labels = np.copy(label_img)
    selem = ball(erosion_radius)

    for lbl in target_labels:
        mask = (label_img == lbl)
        if np.sum(mask) == 0:
            continue
        eroded = erosion(mask, selem)
        split = label(eroded)

        # Assign each recovered connected component a new label ID.
        for region_id in range(1, split.max() + 1):
            submask = (split == region_id)
            recovered = dilation(submask, selem)
            max_label += 1
            new_labels[recovered & (new_labels == lbl)] = max_label

        # Remove any remaining pixels from the original over-merged label.
        new_labels[new_labels == lbl] = 0

    return new_labels
