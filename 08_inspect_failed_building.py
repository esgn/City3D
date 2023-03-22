import trimesh
import sys

ply_patches_dir="data/IGN/ply_extracts/"
obj_dir="data/IGN/obj_footprints/"
results_dir="data/IGN/results/"
failed_file="failed.txt"

with open(failed_file, 'r') as src:
    
    failed_ids = [line.rstrip() for line in src]
    
    for id in failed_ids:
        mesh_file = obj_dir+id+".obj"
        pcd_file = ply_patches_dir+id+".ply"

        scene = trimesh.Scene()
        mesh = trimesh.load_mesh(mesh_file)
        mesh.visual.face_colors = [0,0,255]

        data = trimesh.load(pcd_file)
        pcd_colors=trimesh.visual.color.interpolate(data[:,2], color_map="viridis")
        pcd = trimesh.PointCloud(data.vertices, colors=pcd_colors)
        scene.add_geometry(mesh)
        scene.add_geometry(pcd)
        scene.show(flags={'cull':False})
