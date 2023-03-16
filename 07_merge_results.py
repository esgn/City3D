import trimesh
import os, sys
from statistics import mean

results_dir="data/IGN/results_shifted/"

total_count = 0
broken_count = 0
meshes = []

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

for f in os.listdir(results_dir):
        mesh_file = results_dir+f 
        mesh = trimesh.load_mesh(mesh_file)
        
        trimesh.repair.fix_winding(mesh)
        trimesh.repair.fix_normals(mesh)
        trimesh.repair.broken_faces(mesh)

        if not (mesh.is_watertight):
                broken_count+=1

        meshes.append(mesh)
        total_count+=1

print(str(total_count) + " meshes au total")
print(str(broken_count) + " meshes non étanches")

combined = trimesh.util.concatenate(meshes)
print(combined.center_mass)
obj = combined.export("merged_results.obj")

vertices, normals, faces = read_obj_file("merged_results.obj")
x_mean = mean([v[0] for v in vertices])
y_mean = mean([v[1] for v in vertices])
center = [x_mean,y_mean]
vertices = [[v[0]-x_mean, v[1]-y_mean, v[2]] for v in vertices]

write_obj_file("merged_results_shifted.obj",vertices, normals, faces)