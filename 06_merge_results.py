import trimesh
import os, sys

results_dir="data/IGN/results/"

total_count = 0
broken_count = 0
meshes = []

for f in os.listdir(results_dir):
        mesh_file = results_dir+f       
        mesh = trimesh.load_mesh(mesh_file)
        
        if not (mesh.is_watertight):
                broken_count+=1

        trimesh.repair.fix_winding(mesh)
        trimesh.repair.fix_normals(mesh)
        trimesh.repair.broken_faces(mesh)
        meshes.append(mesh)
        total_count+=1

print(str(total_count) + " meshes au total")
print(str(broken_count) + " meshes non étanches")

combined = trimesh.util.concatenate(meshes)
obj = combined.export("merged_results.obj")
