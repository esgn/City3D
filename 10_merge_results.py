#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os, sys
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
    result_vertices = []
    result_normals = []
    result_faces = []
    args = parse_args()

    for f in tqdm(os.listdir(args.results_dir)):
        mesh_file = os.path.join(args.results_dir, f)
        vertices, normals, faces = read_obj_file(mesh_file)
        shift_index = len(result_vertices)
        result_vertices += vertices
        result_normals += normals
        shifted_faces = shift_faces(faces,shift_index)
        result_faces += shifted_faces
    
    write_obj_file(args.output_file, result_vertices, result_normals, result_faces)

    x_mean = float(round(mean([v[0] for v in result_vertices])))
    y_mean = float(round(mean([v[1] for v in result_vertices])))

    shifted_vertices = [[v[0]-x_mean, v[1]-y_mean, v[2]] for v in result_vertices]
    write_obj_file(args.shifted_output_file, shifted_vertices, result_normals, result_faces)

if __name__ == "__main__":
    main()
