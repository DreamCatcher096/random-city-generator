"""
This Python code preprocesses STL files of 3D building models to optimize their orientation and position.

It loads STL files from an input directory, analyzes the 2D convex hull of the model to find the orientation that
minimizes the bounding area, rotates the model to that optimal orientation, shifts it to sit centered at the origin,
and saves the processed STL models to an output directory.

The main steps are:
1. Loop through all STL files in the input directory
2. For each STL, analyze its 2D convex hull to find the rotation that minimizes bounding area
3. Apply this optimal rotation to the STL
4. Translate the STL to center it at the origin
5. Save the processed STL to the output directory

The goals of the preprocessing are to standardize the orientation of models to make them more consistent, and to
position them centered for easier processing later. This allows the models to be easily loaded and integrated together,
like assembling a 3D city landscape from individual building blocks.

The code uses numpy, scipy, stl, os and tqdm modules.
"""

import os

from tqdm import tqdm
import numpy as np
from scipy.spatial import ConvexHull
from stl import mesh as stlm

# The path to load source STL files
root_path = r'H:\Workspace\OpenfoamGeo\STL_database\beijing_stl\individual'
# The path to save processed STL files
save_path = r'H:\Workspace\OpenfoamGeo\STL_database\beijing_stl\individual_rot'

os.makedirs(save_path, exist_ok=True)

stl_list = os.listdir(root_path)

for stl_name in tqdm(stl_list):
    # Load STL mesh
    stl_mesh = stlm.Mesh.from_file(os.path.join(root_path, stl_name))

    # Get 2D points
    points_2d = np.unique(np.concatenate([stl_mesh.v0, stl_mesh.v1, stl_mesh.v2], axis=0), axis=0)[:, :2]

    # Get convex hull
    tri = ConvexHull(points_2d)

    # Get convex hull vertices
    outline_points = tri.points[tri.vertices, :]

    # Initialize vars to find optimal rotation
    min_bound = np.min(outline_points, axis=0)
    max_bound = np.max(outline_points, axis=0)
    min_area = (max_bound[0] - min_bound[0]) * (max_bound[1] - min_bound[1])
    min_outline = outline_points
    min_R = np.eye(2)
    min_theta = 0

    # Try all vertex pairs to find rotation that minimizes area
    for i in range(outline_points.shape[0] - 1):
        diff = outline_points[i + 1, :] - outline_points[i, :]
        theta = np.arctan(diff[1] / diff[0])
        c, s = np.cos(theta), np.sin(theta)
        R = np.array(((c, -s), (s, c)))

        rot_outline = np.matmul(outline_points, R)

        # Get bounding box
        min_bound = np.min(rot_outline, axis=0)
        max_bound = np.max(rot_outline, axis=0)
        rot_area = (max_bound[0] - min_bound[0]) * (max_bound[1] - min_bound[1])
        if rot_area < min_area:
            min_area = rot_area
            min_outline = rot_outline
            min_R = R
            min_theta = theta

    # Apply optimal rotation
    min_bound = np.min(min_outline, axis=0)
    stl_mesh.rotate([0.0, 0.0, 0.5], min_theta)

    # Translate to center
    stl_mesh.x -= min_bound[0]
    stl_mesh.y -= min_bound[1]

    # Save processed STL
    stl_mesh.save(os.path.join(save_path, stl_name))
