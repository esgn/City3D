import trimesh
import os, sys
from statistics import mean

obj_file="data/building_instances/2_result.obj"

total_count = 0
broken_count = 0
meshes = []


mesh = trimesh.load_mesh(obj_file)
trimesh.repair.fix_winding(mesh)
trimesh.repair.fix_normals(mesh)
trimesh.repair.broken_faces(mesh)
print(mesh.center_mass)
print(mean(mesh.vertices[:,0]))
print(mean(mesh.vertices[:,1]))

mesh.vertices -= mesh.center_mass
print(mesh.is_watertight)
obj = mesh.export("test.obj")
 
# print(mesh.is_watertight)
# print(mesh)
# broken = trimesh.repair.broken_faces(mesh, color=[255,0,0,255])
# print(len(broken))
# mesh.fill_holes()
# broken = trimesh.repair.broken_faces(mesh, color=[255,0,0,255])
# print(len(broken))
# print(mesh.is_watertight)