import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
import skimage.io as io
import skimage
import os
from scipy import ndimage, optimize
from aicsimageio import AICSImage
from skimage.feature import match_template, peak_local_max
from matplotlib import cm
import scipy


def random_cmap():
    """Create a random label colormap with transparent background."""
    np.random.seed(42)
    cmap = matplotlib.colors.ListedColormap (np.random.rand(256,4))
    # value 0 should just be transparent
    cmap.colors[:,3] = 0.5
    cmap.colors[0,:] = 1
    cmap.colors[0,3] = 0

    # if image is a mask, color (last value) should be red
    cmap.colors[-1,0] = 1
    cmap.colors[-1,1:3] = 0
    return cmap


def subtract_background(image, background):
    """Subtract a scalar/background image while preserving unsigned image dtype."""
    dtype = image.dtype
    result = image.astype(np.int32) - background.astype(np.int32)
    return np.clip(result, 0, np.iinfo(dtype).max).astype(dtype)


def DAPI_segmentation_3D(image_path, file_name, results_path, DAPI, Fas3):
    """Watershed-based 3D DAPI segmentation used in early label prototyping."""
    # Load data as a NumPy array.
    data = AICSImage(os.path.join(image_path, file_name))
    img = data.get_image_dask_data("SZYX")
    img = np.array(img)

    # Subtract background from Fas3 and DAPI channels.
    img[DAPI,:,:,:] = skimage.restoration.rolling_ball(img[DAPI,:,:,:], radius=2)
    for i in range(img.shape[1]):
        img[0,i,:,:] = subtract_background(img[Fas3,i,:,:], 20)
        img[DAPI,i,:,:] = subtract_background(img[DAPI,i,:,:], 50)
    
    # Calculate threshold, create mask, and find edges.
    otsu = skimage.filters.threshold_otsu(img[DAPI,:,:,:])
    DAPI_mask = img[DAPI,:,:,:] > otsu

    img_dilate = skimage.morphology.binary_dilation(DAPI_mask, skimage.morphology.ball(9))
    img_dilate = ndimage.binary_fill_holes(img_dilate).astype(int)
    img_dilate = skimage.morphology.binary_erosion(img_dilate, skimage.morphology.ball(5))  
    img_edges = skimage.filters.sobel(img_dilate)

    # Calculate peaks for watershed seeds.
    local_max_indices = peak_local_max(img[DAPI,:,:,:], min_distance=8, threshold_abs=5)

    local_max_indices_array = np.array(local_max_indices)

    depth = local_max_indices_array[:,0]
    rows = local_max_indices_array[:,1]
    columns = local_max_indices_array[:,2]

    local_max = np.array(np.zeros_like(img[DAPI,:,:,:], dtype=bool))
    local_max[depth, rows, columns] = True

    # Perform watershed and save as a TIFF.
    seed_label = skimage.morphology.label(local_max)
    watershed_labels = skimage.segmentation.watershed(image = -img[DAPI,:,:,:],
                                                  markers = seed_label,
                                                  mask=img_dilate)
    

    watershed_edges = skimage.filters.sobel(watershed_labels)
    watershed_edges = skimage.morphology.binary_erosion(watershed_edges, skimage.morphology.ball(1))
    watershed_edges = np.expand_dims(watershed_edges, axis=0)
    
    # Save watershed file.
    io.imsave(os.path.join(results_path, f"{file_name}_watershed_edges.tif"), watershed_edges)


def process_fas3_file(image_path, file_name, suffix, results_path, DAPI, Fas3, dist, abs_thresh):
    import numpy as np
    import matplotlib.pyplot as plt
    from aicsimageio import AICSImage
    from skimage import measure, morphology, segmentation, filters, restoration, feature
    from scipy import ndimage
    import os
    
    #Import image
    data = AICSImage(os.path.join(image_path, file_name + suffix))
    img = data.get_image_dask_data("SZYX")
    img = np.array(img)

    #Subtract background and calculate otsu threshold
    img_p = img.copy()
    img_p[2,:,:,:] = restoration.rolling_ball(img[2,:,:,:], radius=2)
    for i in range(img_p.shape[1]):
        img_p[0,i,:,:] = subtract_background(img[Fas3,i,:,:], 20)
        img_p[2,i,:,:] = subtract_background(img[DAPI,i,:,:], 50)
    
    otsu = filters.threshold_otsu(img_p[DAPI,:,:,:])
    otsu

    #Create DAPI mask, germarium mask (ing_dilate), and germarium outline (img_edges)
    DAPI_mask = img_p[DAPI,:,:,:] > otsu
        
    img_dilate = morphology.binary_dilation(DAPI_mask, morphology.ball(9))
    img_dilate = ndimage.binary_fill_holes(img_dilate).astype(int)
    img_dilate = morphology.binary_erosion(img_dilate, morphology.ball(5))
    img_edges = segmentation.find_boundaries(img_dilate, mode='outer')
    img_edges = morphology.binary_dilation(img_edges, morphology.ball(2))
  
    #Find local maxima, create seed label, and use to make watershed labels
    local_max_indices = feature.peak_local_max(img_p[DAPI,:,:,:], min_distance=dist, threshold_abs=abs_thresh)

    local_max_indices_array = np.array(local_max_indices)
    depth = local_max_indices_array[:,0]
    rows = local_max_indices_array[:,1]
    columns = local_max_indices_array[:,2]
    
    local_max = np.array(np.zeros_like(img_p[Fas3,:,:,:], dtype=bool))
    local_max[depth, rows, columns] = True
    seed_label = morphology.label(local_max)
    
    watershed_labels = segmentation.watershed(image = -img_p[DAPI,:,:,:],
                                                      markers = seed_label,
                                                      mask=img_dilate)
    
    
    #Find which labels touch the edge
    touching_label_ids = set()
    
    for region in measure.regionprops(watershed_labels):
        coords = region.coords
        z, y, x = coords[:, 0], coords[:, 1], coords[:, 2]
        
        # Get only the voxels of this label that touch the edge
        edge_touching_voxels = img_edges[z, y, x]
        
        if np.count_nonzero(edge_touching_voxels) > 0:
            # Get the z-slices where overlap occurs
            touching_z_slices = np.unique(z[edge_touching_voxels])
            
            if len(touching_z_slices) >= 15:
                touching_label_ids.add(region.label)
    
    
    #Separate touching and non-touching labels and merge non-touching labels (germ_cells)
    touching_mask = np.isin(watershed_labels, list(touching_label_ids))
    non_touching_mask = (watershed_labels > 0) & (~touching_mask)
    
    touching_labels = np.zeros_like(watershed_labels)
    non_touching_labels = np.zeros_like(watershed_labels)
    
    touching_labels[touching_mask] = watershed_labels[touching_mask]
    non_touching_labels[non_touching_mask] = watershed_labels[non_touching_mask]
    
    germ_cells = non_touching_labels > 0
    germ_cells = morphology.label(germ_cells)
    
    # Extract mean intensities for each label in touching_labels and set threshold
    mean_intensities = []
    label_ids = []
    
    for region in measure.regionprops(touching_labels, intensity_image=img[Fas3]):
        mean_intensities.append(region.mean_intensity)
        label_ids.append(region.label)
    
    mean_intensities = np.array(mean_intensities)
    threshold = filters.threshold_otsu(mean_intensities)
    
    #Modify the label IDs of labels with high Fas3 signal
    offset = np.max(touching_labels) * 2
    touching_modified = np.zeros_like(touching_labels)
    
    for region in measure.regionprops(touching_labels, intensity_image=img[Fas3]):
        coords = region.coords
        z, y, x = coords[:, 0], coords[:, 1], coords[:, 2]
    
        if region.mean_intensity >= threshold:
            new_label = region.label + offset
        else:
            new_label = region.label
    
        touching_modified[z, y, x] = new_label
    
    #Combine germ cell and touching (i.e. somatic) cell labels
    germ_offset = np.max(touching_modified) #redefine offset so that germ cell and touching labels do not collide
    
    germ_cells, _, _ = segmentation.relabel_sequential(germ_cells)
    germ_cells_offset = np.where(germ_cells > 0, germ_cells + germ_offset, 0)
    
    combined_labels = np.maximum(touching_modified, germ_cells_offset)
    
    n_plots = 48  # how many labels to show
    crop_size = 64  # size of square crop (in XY)
    
    channel_to_show = img[2]  # channel 2
    labels_to_inspect = combined_labels
    
    regions = measure.regionprops(labels_to_inspect)
    
    # Randomly select N regions
    np.random.seed(2)
    regions_to_plot = np.random.choice(regions, size=n_plots, replace=False)
    
    z = combined_labels.shape[0]
    fig, ax = plt.subplots(1, 4, figsize=(18, 6))

    for i in range(4):
        zi = int(z * ((i + 1) / 5))
        ax[i].imshow(combined_labels[zi, :, :], cmap='nipy_spectral', interpolation='nearest')
        ax[i].axis('off')
        ax[i].set_title(f"Z = {zi}")

    # Plot
    n_cols = 4
    n_rows = int(np.ceil(n_plots / n_cols))
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(n_cols*4, n_rows*4))
    
    for ax, region in zip(axes.flat, regions_to_plot):
        zc, yc, xc = map(int, region.centroid)
        zc = np.clip(zc, 0, labels_to_inspect.shape[0] - 1)

        y1 = max(yc - crop_size // 2, 0)
        y2 = min(yc + crop_size // 2, labels_to_inspect.shape[1])
        x1 = max(xc - crop_size // 2, 0)
        x2 = min(xc + crop_size // 2, labels_to_inspect.shape[2])

        # Extract the image and label region
        img_slice = channel_to_show[zc, y1:y2, x1:x2]
        label_crop = labels_to_inspect[zc, y1:y2, x1:x2]

        # Plot background image
        ax.imshow(img_slice, cmap='gray')

        # Plot all label outlines in white
        for label_id in np.unique(label_crop):
            if label_id == 0:
                continue  # skip background
            label_mask = label_crop == label_id
            outline = segmentation.find_boundaries(label_mask, mode='outer')
            color = 'red' if label_id == region.label else 'white'
            ax.contour(outline, colors=color, linewidths=1)

        ax.set_title(f"Label {region.label}")
        ax.axis('off')

    fig.savefig(os.path.join(results_path, file_name + ".pdf"))

    # Convert touching_modified back to label groups
    touching_high = touching_modified > offset
    touching_low = (touching_modified > 0) & ~touching_high
    germ_mask = germ_cells > 0  # binary mask

    # Make sure all masks are uint8 so they become 0 or 1
    germ_mask = germ_mask.astype(np.uint8)
    touching_high = touching_high.astype(np.uint8)
    touching_low = touching_low.astype(np.uint8)

    # Stack them along a new channel axis
    extra_layers = np.stack([germ_mask, touching_high, touching_low], axis=0)  # shape: (3, Z, Y, X)

    # Combine with original image
    combined_image = np.concatenate([img, extra_layers], axis=0)  # shape: (C+3, Z, Y, X)

    # Save as multi-channel TIFF
    stack_5d = np.expand_dims(combined_image, axis=0)
    writers.OmeTiffWriter.save(
        stack_5d.astype(np.uint16),
        os.path.join(results_path, file_name + ".tif"),
        dim_order="TCZYX" 
)


    return(combined_labels)





def ColorLabelsIntensity(labeled_image, props, colormap='viridis', return_projection=False):
    """
    Color a 3D labeled image (Z, Y, X) based on mean_intensity values from regionprops_table.

    Parameters:
    -----------
    labeled_image : np.ndarray
        A 3D (Z, Y, X) label image where each labeled region has a unique integer ID.
    
    props : pandas.DataFrame
        DataFrame with columns 'label' and 'mean_intensity' (e.g. from skimage.measure.regionprops_table).
    
    colormap : str
        Name of the matplotlib colormap to use (default = 'viridis').

    return_projection : bool
        If True, returns a max-intensity projection (Z collapsed to 2D); else returns full RGBA volume.

    Returns:
    --------
    colored_volume : np.ndarray
        A 4D RGBA array (Z, Y, X, 4) or 3D projection (Y, X, 4) depending on `return_projection`.
    """
    assert labeled_image.ndim == 3, "Input label image must be 3D (Z, Y, X)"

    intensity_volume = np.zeros_like(labeled_image, dtype=float)

    for _, row in props.iterrows():
        label_val = row['label']
        intensity = row['mean_intensity']
        intensity_volume[labeled_image == label_val] = intensity

    # Normalize intensity to [0, 1]
    norm = (intensity_volume - intensity_volume.min()) / (intensity_volume.ptp() + 1e-8)

    # Apply colormap
    cmap = cm.get_cmap(colormap)

    if return_projection:
        # Z-projection
        projection = norm.max(axis=0)
        return cmap(projection)  # Shape: (Y, X, 4)
    else:
        # Full 3D RGBA volume
        rgba_volume = np.zeros(labeled_image.shape + (4,), dtype=np.float32)
        for z in range(norm.shape[0]):
            rgba_volume[z] = cmap(norm[z])
        return rgba_volume
    



def merge_channels(image1, image2):
    """
    Merge two 3D or 4D images (Z, Y, X) or (C, Z, Y, X) into a single 4D image (C, Z, Y, X).
    
    Parameters:
    ----------
    image1 : np.ndarray
        First 3D or 4D image.
        
    image2 : np.ndarray
        Second 3D or 4D image.
        
    Returns:
    -------
    merged_image : np.ndarray
        Merged 4D image.
    """
    assert image1.shape[-2:] == image2.shape[-2:]
    f"Image dimensions do not match: {image1.shape[-2:]} vs {image2.shape[-2:]}"

    if image1.ndim > 3 | image2.ndim > 3:
        merged_image = np.concatenate((image1, image2), axis=0)
    else:
        merged_image = np.stack((image1, image2), axis=-1)  # Shape: (Z, Y, X, 2)
    
    return merged_image





def attenuation_correction(stack, fit_func='exponential', normalize_to_first=True):
    """
    Apply attenuation correction to a Z-stack using a fit on slice-wise Otsu thresholds.

    Parameters:
    - stack: np.ndarray of shape (Z, Y, X)
    - fit_func: 'exponential' or 'polynomial'
    - normalize_to_first: If True, normalize gain relative to the first slice

    Returns:
    - corrected_stack: np.ndarray, same shape and dtype as input
    - profile: dict with raw thresholds, fitted curve, and correction factors
    """
    # Get dtype of the input stack and convert to 16-bit if necessary
    dtype = stack.dtype
    if dtype != np.uint16:
        stack = stack.astype(np.uint16)

    # Compute Otsu threshold per slice
    z_vals = np.arange(stack.shape[0])
    otsu_thresholds = np.array([skimage.filters.threshold_otsu(slice) for slice in stack])

    # Fit a curve to the thresholds
    if fit_func == 'exponential':
        def model(z, a, b): return a * np.exp(-b * z)
        popt, _ = scipy.optimize.curve_fit(model, z_vals, otsu_thresholds, p0=(otsu_thresholds[0], 0.01))
        fitted = model(z_vals, *popt)
    elif fit_func == 'polynomial':
        coeffs = np.polyfit(z_vals, otsu_thresholds, deg=2)
        fitted = np.polyval(coeffs, z_vals)
    else:
        raise ValueError("fit_func must be 'exponential' or 'polynomial'")

    # Compute correction factors
    if normalize_to_first:
        gain = fitted[0] / (fitted + 1e-8)
    else:
        gain = 1.0 / (fitted + 1e-8)

    # Apply correction and convert back to original dtype
    corrected = np.clip((stack.astype(np.int32) * gain[:, None, None]), 0, np.iinfo(dtype).max)

    return corrected, {
        "z": z_vals,
        "otsu_thresholds": otsu_thresholds,
        "fitted_curve": fitted,
        "gain_factors": gain
    }
