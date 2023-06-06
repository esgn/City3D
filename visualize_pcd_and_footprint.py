import pyvista as pv    
import os, sys
import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--building_id", default="BATIMENT0000000320899175",
                        help="Unique building id")
    return parser.parse_args()

def main():
    args = parse_args()
    pcd_file = "data/IGN/point_cloud_extracts_ply_shifted/"+args.building_id+".ply"
    footprint_file = "data/IGN/footprints_obj_shifted_fixed/"+args.building_id+".obj"
    plotter = pv.Plotter()
    plotter.background_color = "white"
    pcd = pv.read(pcd_file)
    plotter.add_mesh(pcd, color='blue', smooth_shading=True)
    footprint = pv.read(footprint_file)
    plotter.add_mesh(footprint, color='red', smooth_shading=True)
    plotter.show()

if __name__ == "__main__":
    main()
