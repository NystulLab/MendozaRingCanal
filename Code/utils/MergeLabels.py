import numpy as np
from skimage.measure import regionprops
from skimage.measure import label as sklabel
from itertools import combinations


def get_3d_bounding_boxes(label_image):
    """Return 3D bounding boxes as label -> (z0, z1, y0, y1, x0, x1)."""
    props = regionprops(label_image)
    boxes = {}
    for prop in props:
        z0, y0, x0, z1, y1, x1 = prop.bbox
        boxes[prop.label] = (z0, z1, y0, y1, x0, x1)
    return boxes


def shrink_bbox(bbox, shrink_factors=(0.5, 0.5)):
    """Shrink a box along its two shortest axes before overlap testing."""
    z0, z1, y0, y1, x0, x1 = bbox
    lengths = np.array([(z1 - z0), (y1 - y0), (x1 - x0)])
    sorted_idx = np.argsort(lengths)

    # Ring-canal labels are thin in two axes, so shrinking these axes prevents
    # broad bounding boxes from merging labels that are merely nearby.
    shrink_dims = sorted_idx[:2]
    coords = np.array([[z0, z1], [y0, y1], [x0, x1]])

    for i, dim in enumerate(shrink_dims):
        center = np.mean(coords[dim])
        half = (coords[dim][1] - coords[dim][0]) * shrink_factors[i] / 2
        coords[dim] = [int(center - half), int(center + half)]

    return tuple(coords.flatten())


def boxes_intersect(b1, b2):
    """Check if two 3D boxes intersect."""
    z0a, z1a, y0a, y1a, x0a, x1a = b1
    z0b, z1b, y0b, y1b, x0b, x1b = b2
    return not (z1a <= z0b or z1b <= z0a or
                y1a <= y0b or y1b <= y0a or
                x1a <= x0b or x1b <= x0a)


def MergeLabels(label_image, shrink_factors=(0.5, 0.5)):
    """Merge labels whose shrunken 3D bounding boxes still overlap.

    This is a post-processing step for StarDist outputs that occasionally split
    a single follicle-cell boundary into adjacent label IDs.
    """
    # Relabel first so downstream merge IDs are contiguous and predictable.
    label_image = sklabel(label_image)

    boxes = get_3d_bounding_boxes(label_image)
    shrunk_boxes = {label: shrink_bbox(bbox, shrink_factors) for label, bbox in boxes.items()}

    # Union-find tracks connected groups of labels that should be merged.
    parent = {label: label for label in shrunk_boxes}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        root_x, root_y = find(x), find(y)
        if root_x != root_y:
            parent[root_y] = root_x

    # Any intersecting shrunken boxes are treated as one segmented object.
    for a, b in combinations(shrunk_boxes.keys(), 2):
        if boxes_intersect(shrunk_boxes[a], shrunk_boxes[b]):
            union(a, b)

    label_map = {label: find(label) for label in parent}

    merged_image = np.zeros_like(label_image)
    for old_label, new_label in label_map.items():
        merged_image[label_image == old_label] = new_label

    return sklabel(merged_image)
