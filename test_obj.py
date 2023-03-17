import pyvista as pv    
import os, sys

# a possibly problematic result
obj_file="BATIMENT0000000320898295.obj"

mesh = pv.read(obj_file)
print(mesh)