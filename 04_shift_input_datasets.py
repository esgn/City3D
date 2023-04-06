#!/usr/bin/env python
# -*- coding:utf-8 -*-

import open3d as o3d
import os
from tqdm import tqdm
from utils import *
import argparse

# This script processes the input datasets and apply a global shift to them
# In details:
# - The center of each point cloud extract is calculated
# - The center coordinate is used to shift the point cloud extract and the corresponding footprint
# - Then center coordinates are saved in a .origin file for each building
# Warning : Altitudes are not shifted by this script

def parse_args():
    parser = argparse.ArgumentParser("Apply a global shift to point cloud ply and footprint obj files")

    parser.add_argument("--input_footprints_dir", "-f",
                        help="Input footprints as separate obj files", default="data/IGN/footprints_obj")
    parser.add_argument("--output_footprints_dir", "-g",
                        help="Output directory for shifted footprints", default="data/IGN/footprints_obj_shifted")
    parser.add_argument("--input_pcd_extracts_dir", "-p",
                        help="Input point cloud extracts as separate ply files", default="data/IGN/point_cloud_extracts_ply")
    parser.add_argument("--output_pcd_extracts_dir", "-q",
                        help="Output directory for point cloud extracts", default="data/IGN/point_cloud_extracts_ply_shifted")
    parser.add_argument("--output_origins_dir", "-o",
                        help="Output directory for origin files", default="data/IGN/origin_shift")

    return parser.parse_args()

def main():
    args = parse_args()

    recreate_dir(args.output_pcd_extracts_dir)
    recreate_dir(args.output_footprints_dir)
    recreate_dir(args.output_origins_dir)

    for f in tqdm(os.listdir(args.input_pcd_extracts_dir)):
        # building identifier
        cleabs = f.split(".")[0]
        # read poincloud patch ply file
        pcd = o3d.io.read_point_cloud(os.path.join(args.input_pcd_extracts_dir, f))
        # get point cloud center
        center = pcd.get_center()
        # We keep only x and y center as we dont want to shift altitudes
        center[2] = 0
        # shift point cloud
        pcd.translate(center*-1, relative=True)
        # write resulting point cloud with global shift
        o3d.io.write_point_cloud(os.path.join(args.output_pcd_extracts_dir, f), pcd, write_ascii=True)
        # load obj footprint file
        vertices, normals, faces = read_obj_file(os.path.join(args.input_footprints_dir, cleabs+".obj"))
        # write obj footprint file with global shift
        write_obj_file(os.path.join(args.output_footprints_dir, cleabs+".obj"), vertices-center, normals, faces)
        # write center coordinates in a .origin file
        with open(os.path.join(args.output_origins_dir, cleabs+".origin"),'w') as origin:
               center = center
               origin.write(' '.join(str(x) for x in center))

if __name__ == "__main__":
    main()
