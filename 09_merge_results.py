#!/usr/bin/env python
# -*- coding:utf-8 -*-

import trimesh
import os
from statistics import mean
from tqdm import tqdm
from utils import *
import argparse

def parse_args():
    parser = argparse.ArgumentParser("Import all results in a single obj model")
    parser.add_argument("--results_dir", "-r",
                        help="Input directory containing fixed city3d results", default="data/IGN/results_shifted/")
    parser.add_argument("--output_file", "-o",
                        help="Output file containing all results", default="data/IGN/merged_results.obj")
    parser.add_argument("--shifted_output_file", "-s",
                        help="Output file containing all results in local coordinates", default="data/IGN/merged_results_shifted.obj")
    return parser.parse_args()    

def main():

    total_count = 0
    broken_count = 0
    meshes = []
    args = parse_args()
    
    for f in tqdm(os.listdir(args.results_dir)):
        mesh_file = os.path.join(args.results_dir, f)
        mesh = trimesh.load_mesh(mesh_file)
        if not (mesh.is_watertight):
                broken_count+=1
        meshes.append(mesh)
        total_count+=1

    print(str(total_count) + " total meshes")
    print(str(broken_count) + " non watertight mesh")

    combined = trimesh.util.concatenate(meshes)
    combined.export(args.output_file)

    vertices, normals, faces = read_obj_file(args.output_file)
    x_mean = float(round(mean([v[0] for v in vertices])))
    y_mean = float(round(mean([v[1] for v in vertices])))
    vertices = [[v[0]-x_mean, v[1]-y_mean, v[2]] for v in vertices]

    write_obj_file(args.shifted_output_file, vertices, normals, faces)

if __name__ == "__main__":
    main()
