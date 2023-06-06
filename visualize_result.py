import pyvista as pv    
import os, sys
import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--file_path", default="data/IGN/results/BATIMENT0000000320899175.obj",
                        help="3D model file path")
    return parser.parse_args()

def main():
    args = parse_args()
    result_file = args.file_path
    plotter = pv.Plotter()
    plotter.background_color = "white"
    pcd = pv.read(result_file)
    plotter.add_mesh(pcd, color='yellow', smooth_shading=True)
    plotter.show()

if __name__ == "__main__":
    main()
