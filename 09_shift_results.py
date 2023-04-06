#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os,sys
from tqdm import tqdm
from utils import *
import argparse

# This scripts takes the building reconstructed by City3D
# and shift to them to their original position
       
def parse_args():
    parser = argparse.ArgumentParser("Shift back the results to Lambert 93 coordinates")
    parser.add_argument("--results_dir", "-r",
                        help="Input directory containing fixed city3d results", default="data/IGN/results_fixed_with_cgal")
    parser.add_argument("--origins_dir", "-s",
                        help="Input directory containing origin files", default="data/IGN/origin_shift")
    parser.add_argument("--output_dir", "-o",
                        help="Output directory for shifted results", default="data/IGN/results_shifted")
    return parser.parse_args()    

def main():
    args = parse_args()
    recreate_dir(args.output_dir)
    for f in tqdm(os.listdir(args.results_dir)):
        cleabs = f.split(".")[0]
        # read building obj file
        vertices, normals, faces = read_obj_file(os.path.join(args.results_dir,f))
        # read center file
        c = read_origin(os.path.join(args.origins_dir, cleabs+".origin"))
        # add origin coordinates to x and y model coordinates
        vertices = [[v[0]+c[0],v[1]+c[1],v[2]] for v in vertices]
        # write obj file with shift
        write_obj_file(os.path.join(args.output_dir,cleabs+".obj"), vertices, normals, faces)

if __name__ == "__main__":
    main()
