import os, sys
from statistics import mean
import shutil

# This scripts takes the building reconstructed by City3D
# and shift to them to their original position

results_dir="data/IGN/results/"
output_dir="data/IGN/results_shifted/"
origins_dir="data/IGN/origin_shift/"

def recreate_dir(output_dir):
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.mkdir(output_dir)

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

def read_origin(filepath):
        fline=open(filepath).readline().rstrip()       
        center = [float(x) for x in fline.split(' ')]
        return center
       
def main():
        recreate_dir(output_dir)
        for f in os.listdir(results_dir):
                cleabs = f.split(".")[0]
                # read building obj file
                vertices, normals, faces = read_obj_file(results_dir+f)
                # read center file
                c = read_origin(origins_dir+cleabs+".origin")
                # add origin coordinates to x and y model coordinates
                vertices = [[v[0]+c[0],v[1]+c[1],v[2]] for v in vertices]
                # write obj file with shift
                write_obj_file(output_dir+cleabs+".obj", vertices, normals, faces)

if __name__ == "__main__":
    main()
