import pyvista as pv    
import os, sys

# a possibly problematic result
obj_file="data/IGN/results/BATIMENT0000000320899175.obj"

mesh = pv.read(obj_file)
mesh.plot()