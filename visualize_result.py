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
    result_file = "data/IGN/results/"+args.building_id+".obj"
    plotter = pv.Plotter()
    plotter.background_color = "white"
    pcd = pv.read(result_file)
    plotter.add_mesh(pcd, color='yellow', smooth_shading=True)
    plotter.show()

if __name__ == "__main__":
    main()
