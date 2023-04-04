#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys, os
import argparse
from tqdm import tqdm
import numpy as np
from utils import *
import pdal
from shapely.geometry import Polygon
from shapely import force_2d

def parse_args():
    parser = argparse.ArgumentParser("Export gpkg polygons file to OBJ files")

    parser.add_argument("--input_footprints_dir", "-f",
                        help="Input footprints as obj files", default="data/IGN/footprints_obj_shifted")
    parser.add_argument("--input_pcd_extracts_dir", "-p",
                        help="Input point cloud extracts as ply files", default="data/IGN/point_cloud_extracts_ply_shifted")
    parser.add_argument("--output_dir", "-o",
                        help="Output directory of footprints with z fixed", default="data/IGN/footprints_obj_shifted_fixed")

    return parser.parse_args()

def main():

    args = parse_args()
    recreate_dir(args.output_dir)
    count = 0
    for f in tqdm(os.listdir(args.input_pcd_extracts_dir)):
        # building identifier
        cleabs = f.split(".")[0]
        # Load min_z from obj 
        vertices, normals, faces = read_obj_file( os.path.join(args.input_footprints_dir, cleabs+".obj") )
        z_obj =  min([v[2] for v in vertices])
        polygon = force_2d(Polygon(vertices))

        pipeline = pdal.Reader( os.path.join(args.input_pcd_extracts_dir,f) )
        pipeline |= pdal.Filter.crop(polygon=polygon.wkt)
        pipeline |= pdal.Filter.locate(dimension="Z", minmax="min")
        pipeline.execute()
        try:
            z_pcd_min = pipeline.arrays[0][0][2]
        except:
            print("CROPPING ISSUE WITH FOOTPRINT WITH NO BUFFER ON " + cleabs)
            write_obj_file(os.path.join(args.output_dir,cleabs+".obj"),vertices, normals, faces)
            continue
        if z_pcd_min < z_obj:
            count+=1
            for index, vz in enumerate(vertices):
                vertices[index][2] = (z_pcd_min-0.5)
        
        write_obj_file(os.path.join(args.output_dir,cleabs+".obj"),vertices, normals, faces)
    print(str(count) + " footprints files have been fixed")
            
if __name__ == "__main__":
    main()
