import os
import shutil

def recreate_dir(output_dir):
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.mkdir(output_dir)

def read_obj_file(filepath):
    vertices, normals, faces = [],[],[]
    with open(filepath) as src:
        while True:
            line = src.readline()
            if not line: 
                break
            else:
                line = line.rstrip()
            if line.startswith("v "):
                c=line.split()[1:]
                vertices.append([float(x) for x in c])
            if line.startswith("vn "):
                c=line.split()[1:]
                normals.append([int(x) for x in c])
            if line.startswith("f "):
                line = " ".join(line.split())
                c=line.split()[1:]
                faces.append([str(x) for x in c])
    return vertices, normals, faces

# face_format
# 0 : vertex
# 1 : vertex/vertex_texture
# 2 : vertex/vertex_normal
def write_obj_file(filepath, vertices, normals, faces, face_format=0):
    with open(filepath,'w') as dst:
        for vertex in vertices:
            vx = ["v"] + list(str(v) for v in vertex)
            dst.write(' '.join(vx)+"\n")
        for normal in normals:
            nl = ["vn"] + list(str(n) for n in normal)
            dst.write( ' '.join(nl)+"\n")
        for face in faces:
            if face_format==0:
                fc = ['f'] + list(str(f) for f in face)
            elif face_format==1:
                fc = ['f'] + list(str(f)+'/'+str(f) for f in face)
            elif face_format==2:
                fc = ['f'] + list(str(f)+'//'+str(f) for f in face)
            dst.write( ' '.join(fc)+"\n")

def read_origin(filepath):
    fline=open(filepath).readline().rstrip()       
    center = [float(x) for x in fline.split(' ')]
    return center

def shift_faces(faces, shift_index):
    shifted_faces = []
    for face in faces:
        shifted_face = []
        for f in face:
            if '//' in f:
                index = int(f.split('//')[0])
                index+=shift_index
                index = str(index) + '//' + str(index)
            elif '/' in f:
                index = int(f.split('/')[0])
                index+=shift_index
                index = str(index) + '/' + str(index)
            else:
                index=int(f)
                index+=shift_index
            shifted_face.append(index)
        shifted_faces.append(shifted_face)
    return shifted_faces

def write_merged_obj_files(obj_files_dir, merged_obj_filename):
    merged_vertices = []
    merged_normals = []
    merged_faces = []
    for f in os.listdir(obj_files_dir):
        mesh_file = os.path.join(obj_files_dir, f)
        vertices, normals, faces = read_obj_file(mesh_file)
        shift_index = len(merged_vertices)
        merged_vertices += vertices
        merged_normals += normals
        shifted_faces = shift_faces(faces,shift_index)
        merged_faces += shifted_faces
    write_obj_file(merged_obj_filename, merged_vertices, merged_normals, merged_faces)
