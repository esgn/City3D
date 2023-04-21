#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os,sys
from tqdm import tqdm
from statistics import mean
from utils import *
import shutil

# This scripts takes the building reconstructed by City3D
# and shift to them to their original position

results_dir="data/IGN/results_simplified/"
output_dir="data/IGN/results_shifted/"
origins_dir="data/IGN/origin_shift/"
       
def main():
    recreate_dir(output_dir)
    for f in tqdm(os.listdir(results_dir)):
        cleabs = f.split(".")[0]
        # read building obj file
        vertices, normals, faces = read_obj_file(results_dir+f)
        # read center file
        c = read_origin(origins_dir+cleabs+".origin")
        # add origin coordinates to x and y model coordinates
        vertices = [[v[0]+c[0],v[1]+c[1],v[2]] for v in vertices]
        # write obj file with shift
        write_obj_file(output_dir+cleabs+".obj", vertices, normals, faces)

if __name__ == "__main__":
    main()
