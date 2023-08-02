"""
This code procedurally generates 3D city scenes by packing random building STL models.

It loads building STL models, randomly rotates and positions them. Then it uses the rectpack module to pack models into
subsections of a city block. Multiple city blocks with randomized building arrangements are generated.

The code does the following:

1. Load and preprocess building STL models
2. Define city parameters
3. Loop to generate multiple city scenes

The output is a directory containing multiple city scenes, each with randomized building arrangements.
"""

import copy
import math
import os
import random

import numpy as np
import rectpack
from stl import mesh as stlm
from tqdm import tqdm

# Set random seeds for reproducibility
random.seed(0)
np.random.seed(0)

# The directory that contains individual building models
root_path = './buildings'
# The path to save the generated city scenes
save_path = './outputs'
os.makedirs(save_path, exist_ok=True)

# the unit is set to meters
scene_num = 500  # Number of city scenes to generate
domain_size = 200  # Total size of city domain
box_margin_factor = 2  # Packing margin around buildings
lane_width = 15  # Width of lanes between city subsections
sub_sections = (2, 2)  # Number of subsections along x and y
min_space = 10  # Minimum space between packed buildings

# Building rotation angles
rot_angle = [0, 90, 180, 270]

# Load and preprocess building STLs
mesh_list = []
for stl_name in os.listdir(root_path):
    mesh = stlm.Mesh.from_file(os.path.join(root_path, stl_name))
    # Filter small STLs
    if np.any(mesh.max_ < 4):
        continue
    # Randomly rotate
    random_angle = random.choice(rot_angle)
    mesh.rotate([0.0, 0.0, 0.5], math.radians(random_angle))

    # Shift to origin
    mesh.x -= np.min(mesh.x)
    mesh.y -= np.min(mesh.y)

    # Update bounds
    mesh.max_[0] = np.max(mesh.x)
    mesh.max_[1] = np.max(mesh.y)

    mesh_list.append(mesh)

random.shuffle(mesh_list)

# Generate multiple city scenes
global_index = 0
for i in tqdm(range(scene_num)):
    sub_sections = np.random.randint(1, 3, size=2)
    # Create subfolder for this scene
    curr_save_path = os.path.join(save_path, 'scene_%s' % (i + 1))
    os.makedirs(curr_save_path, exist_ok=True)

    # Split scene into subsections
    sub_length = (domain_size - (sub_sections[0] - 1) * lane_width) / sub_sections[0]
    sub_width = (domain_size - (sub_sections[1] - 1) * lane_width) / sub_sections[1]

    # Add subsection areas
    sub_areas = []
    for i_s in range(sub_sections[0]):
        for j_s in range(sub_sections[1]):
            sub_areas.append([i_s * (sub_length + lane_width), j_s * (sub_width + lane_width), sub_length, sub_width])

    building_idx = 0
    saved = False  # Flag if any buildings saved

    # Loop through subsections
    for i_sub, sub_area in enumerate(sub_areas):
        save_mesh_list = []
        # Create packer
        rect_packer = rectpack.newPacker(
            mode=rectpack.PackingMode.Offline,
            pack_algo=rectpack.MaxRectsBlsf,
            sort_algo=rectpack.SORT_NONE,
            bin_algo=rectpack.PackingBin.BBF,
            rotation=False,
        )
        rect_list = []
        total_area = 0  # Total packed area
        # Add random buildings until subsection is full
        while True:
            max_bound = mesh_list[global_index].max_[:2].copy()
            region_bound = max_bound + min_space + np.random.rand(2) * box_margin_factor
            # Check if building fits
            if total_area + region_bound[0] * region_bound[1] > sub_area[-2] * sub_area[-1]:
                if len(rect_list) == 0:
                    global_index += 1
                    if global_index >= len(mesh_list):
                        # random.shuffle(mesh_list)
                        global_index = 0
                    continue
                else:
                    break

            total_area += region_bound[0] * region_bound[1]
            rect_list.append([region_bound[0], region_bound[1], global_index])
            global_index += 1
            if global_index >= len(mesh_list):
                # random.shuffle(mesh_list)
                global_index = 0

        # Pack rectangles
        for rid, rect_ele in enumerate(rect_list):
            rect_packer.add_rect(width=rect_ele[0], height=rect_ele[1], rid=rect_ele[2])
        rect_packer.add_bin(width=sub_area[-2], height=sub_area[-1])
        rect_packer.pack()

        area_bound = [0, 0, 0, 0]
        if len(rect_packer) == 0:
            packer_res = [[0, 0, rect_ele[0], rect_ele[1], rect_ele[2]]]
        else:
            packer_res = [r for r in rect_packer[0].rect_list()]

        # Add packed buildings
        for r in packer_res:
            curr_mesh = copy.deepcopy(mesh_list[r[-1]])
            mesh_bound = curr_mesh.max_[:2]
            offset_x = 0.5 * (r[2] - mesh_bound[0])
            offset_y = 0.5 * (r[3] - mesh_bound[1])
            curr_mesh.x += r[0] + sub_area[0] + offset_x
            curr_mesh.y += r[1] + sub_area[1] + offset_y
            if r[0] < area_bound[0]:
                area_bound[0] = r[0]
            if r[1] < area_bound[1]:
                area_bound[1] = r[1]
            if r[2] + r[0] > area_bound[2]:
                area_bound[2] = r[2] + r[0]
            if r[3] + r[1] > area_bound[3]:
                area_bound[3] = r[3] + r[1]
            # curr_mesh.save(os.path.join(curr_save_path, 'building_sub_%s_%s.stl' % (i_sub, building_idx)))
            save_mesh_list.append(curr_mesh)

        # Center subsection in full scene
        offset_x = (sub_area[-2] / 2) - ((area_bound[2] - area_bound[0]) / 2)
        offset_y = (sub_area[-1] / 2) - ((area_bound[3] - area_bound[1]) / 2)

        # Save buildings
        for save_mesh in save_mesh_list:
            save_mesh.x += offset_x - (domain_size / 2)
            save_mesh.y += offset_y - (domain_size / 2)
            save_mesh.save(os.path.join(curr_save_path, 'building_%s.stl' % building_idx))
            saved = True
            building_idx += 1

    if not saved:  # If the defined area is too small, it might not be able to find buildings to fit in
        print('scene %s warning empty scene' % (i + 1))
