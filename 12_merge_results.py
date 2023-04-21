#!/usr/bin/env python
# -*- coding:utf-8 -*-

import trimesh
import os
from statistics import mean
from tqdm import tqdm
from utils import *

results_dir="data/IGN/results_shifted/"
output_file="merged_results.obj"
shifted_output_file="merged_results_shifted.obj"


def main():

    total_count = 0
    broken_count = 0
    meshes = []
    
    for f in tqdm(os.listdir(results_dir)):
        mesh_file = results_dir+f 
        mesh = trimesh.load_mesh(mesh_file)
        if not (mesh.is_watertight):
                broken_count+=1
        meshes.append(mesh)
        total_count+=1

    print(str(total_count) + " meshes au total")
    print(str(broken_count) + " meshes non étanches")

    combined = trimesh.util.concatenate(meshes)
    print(combined.center_mass)
    obj = combined.export(output_file)

    vertices, normals, faces = read_obj_file(output_file)
    x_mean = mean([v[0] for v in vertices])
    y_mean = mean([v[1] for v in vertices])
    center = [x_mean,y_mean]
    vertices = [[v[0]-x_mean, v[1]-y_mean, v[2]] for v in vertices]

    write_obj_file(shifted_output_file, vertices, normals, faces)

if __name__ == "__main__":
    main()
