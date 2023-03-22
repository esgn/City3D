import open3d as o3d
import os
from statistics import mean
from tqdm import tqdm
from utils import *

# This script processes the input datasets and apply a global shift to them
# In details:
# - The center of each point cloud patch is calculated
# - The center coordinates are used to shift the point cloud patch and the corresponding footprint
# - Then center coordinates are saved in a .origin file
# Altitudes are not shifted by this script

root_dir = os.path.join("data", "IGN")
ply_dir = os.path.join(root_dir, "ply_extracts")
obj_dir = os.path.join(root_dir, "obj_footprints")
output_ply_dir = os.path.join(root_dir, "ply_extracts_shifted")
output_obj_dir = os.path.join(root_dir, "obj_footprints_shifted")
output_origin_dir = os.path.join(root_dir, "origin_shift")

def main():

    recreate_dir(output_ply_dir)
    recreate_dir(output_obj_dir)
    recreate_dir(output_origin_dir)

    for f in tqdm(os.listdir(ply_dir)):
        # building identifier
        cleabs = f.split(".")[0]
        # read poincloud patch ply file
        pcd = o3d.io.read_point_cloud(os.path.join(ply_dir, f))
        # get point cloud center
        center = pcd.get_center()
        # We keep only x and y center as we dont want to shift altitudes
        center[2] = 0
        # shift point cloud
        pcd.translate(center*-1, relative=True)
        # write resulting point cloud with global shift
        o3d.io.write_point_cloud(os.path.join(output_ply_dir, f), pcd, write_ascii=True)
        # load obj footprint file
        vertices, normals, faces = read_obj_file(os.path.join(obj_dir, cleabs+".obj"))
        # write obj footprint file with global shift
        write_obj_file(os.path.join(output_obj_dir, cleabs+".obj"), vertices-center, normals, faces)
        # write center coordinates in a .origin file
        with open(os.path.join(output_origin_dir, cleabs+".origin"),'w') as origin:
               center = center
               origin.write(' '.join(str(x) for x in center))

if __name__ == "__main__":
    main()
