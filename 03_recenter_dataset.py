import open3d as o3d
import os, sys
from statistics import mean
import numpy as np
import shutil

# This script processes the input datasets and apply a global shift to them
# to set a new origin at model center

ply_dir="data/IGN/ply_extracts/"
obj_dir="data/IGN/obj_footprints/"
output_ply_dir="data/IGN/ply_extracts_shifted/"
output_obj_dir="data/IGN/obj_footprints_shifted/"
output_origin_dir="data/IGN/origin_shift/"

def recreate_dir(output_dir):
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.mkdir(output_dir)

# Read obj file using basic python 
def read_obj_file(filepath):
        vertices, normals, faces = [],[],[]
        with open(filepath) as src:
                line = src.readline().rstrip()
                while line:
                        if line.startswith("v "):
                                c=line.split(' ')[1:]
                                vertices.append([float(x) for x in c])
                        if line.startswith("vn "):
                                c=line.split(' ')[1:]
                                normals.append([int(x) for x in c])
                        if line.startswith("f "):
                                c=line.split(' ')[1:]
                                faces.append([str(x) for x in c])
                        line = src.readline().rstrip()
        return vertices, normals, faces

# Write obj file using basic python 
def write_obj_file(filepath, vertices, normals, faces):
        with open(filepath,'w') as dst:
                for vertex in vertices:
                        vx = ["v"] + list(str(v) for v in vertex)
                        dst.write(' '.join(vx)+"\n")
                for normal in normals:
                        nl = ["vn"] + list(str(n) for n in normal)
                        dst.write( ' '.join(nl)+"\n")
                for face in faces:
                        fc = ['f'] + list(str(f) for f in face)
                        dst.write( ' '.join(fc)+"\n")

def main():
        recreate_dir(output_ply_dir)
        recreate_dir(output_obj_dir)
        recreate_dir(output_origin_dir)
        for f in os.listdir(ply_dir):
                cleabs = f.split(".")[0]
                # read poincloud patch ply file
                pcd = o3d.io.read_point_cloud(ply_dir+f)
                # get point cloud center
                center = pcd.get_center()
                # We keep only x and y center as we dont want to shift altitudes
                center[2] = 0
                pcd.translate(center*-1,relative=True)
                # write resulting ply with global shift
                o3d.io.write_point_cloud(output_ply_dir+f, pcd, write_ascii=True)
                # load obj footprint file
                vertices, normals, faces = read_obj_file(obj_dir+cleabs+".obj")
                # write obj footprint file with global shift
                write_obj_file(output_obj_dir+cleabs+".obj", vertices-center, normals, faces)
                with open(output_origin_dir+cleabs+".origin",'w') as origin:
                       center = center
                       origin.write(' '.join(str(x) for x in center))

if __name__ == "__main__":
    main()
