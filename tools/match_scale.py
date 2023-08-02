"""This is the code for matching different building models

Sometimes when we get the models of buildings, they may not come with the same scale. This code is for matching the
scale of two groups of stl models, according to the referencing group. The scale reference is based on height,
which means the goal of this code is to adjust the target model group so that the maximum height of the buildings is
aligned with the maximum building height of the reference group """

import os

from tqdm import tqdm
from stl import mesh as stlm

# set the path to the group of models to be rescaled
target_path = ''
# set the path to the group of models for referencing
ref_path = ''
# the path to save the rescaled models
save_path = ''

os.makedirs(save_path, exist_ok=True)

target_mesh_list = []
target_max_height = 0
stl_list = os.listdir(target_path)  # assume that the directory contains only the stl files
for stl_name in stl_list:
    stl_mesh = stlm.Mesh.from_file(os.path.join(target_path, stl_name))
    if target_max_height < stl_mesh.max_[-1]:
        target_max_height = stl_mesh.max_[-1]
    target_mesh_list.append(stl_mesh)

ref_mesh_list = []
ref_max_height = 0
stl_list = os.listdir(ref_path)  # assume that the directory contains only the stl files
for stl_name in stl_list:
    stl_mesh = stlm.Mesh.from_file(os.path.join(ref_path, stl_name))
    if ref_max_height < stl_mesh.max_[-1]:
        ref_max_height = stl_mesh.max_[-1]
    ref_mesh_list.append(stl_mesh)

idx = 0
for mesh in tqdm(target_mesh_list):
    mesh.x *= ref_max_height / target_max_height
    mesh.y *= ref_max_height / target_max_height
    mesh.z *= ref_max_height / target_max_height
    mesh.save(os.path.join(save_path, 'building_%s.stl' % idx))
    idx += 1
