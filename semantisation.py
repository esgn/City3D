from utils import *
import glob
import random
import math
import json

from cjio import cityjson
from cjio.models import CityObject, Geometry


RESULTS_DIR="/home/FGeniet/data_storage/AD_jumeaux_numeriques/result/Semantisation/res/"
input_folder = '/home/FGeniet/data_storage/AD_jumeaux_numeriques/result/Semantisation/obj/results_shifted/'
normalesFile = '/home/FGeniet/data_storage/AD_jumeaux_numeriques/result/Semantisation/res/'

objFiles = glob.glob(input_folder+'*.obj')
cm = cityjson.CityJSON()

fileNormales = open(RESULTS_DIR+'normales.txt','w')

def computeNormal(f,vertices):
    norme_n = 0
    cp = []

    while (norme_n==0):
        i1,i2,i3 = choosePoints(f)
        p1,p2,p3 = vertices[int(i1.split('/')[0])-1],vertices[int(i2.split('/')[0])-1],vertices[int(i3.split('/')[0])-1]

        v1 = [p2[0]-p1[0],p2[1]-p1[1],p2[2]-p1[2]]
        v2 = [p3[0]-p1[0],p3[1]-p1[1],p3[2]-p1[2]]
        cp = crossProduct(v1,v2)
        norme_n = norme(cp)

    n = normalize(cp)
    return n

def computeBBextent(pts):
    [x_min, y_min, z_min] = pts[0]
    x_max, y_max, z_max = x_min, y_min, z_min

    for p in pts:
        if(p[0]>x_max):
            x_max = p[0]
        if(p[1]>y_max):
            y_max = p[1]
        if(p[2]>z_max):
            z_max = p[2]
            
        if(p[0]<x_min):
            x_min = p[0]
        if(p[1]<y_min):
            y_min = p[1]
        if(p[2]<z_min):
            z_min = p[2]
            
    return norme([x_max-x_min, y_max-y_min, z_max-z_min])

def semanticType(face_p, face_n,z_min):
    [nx,ny,nz]=[abs(face_n[0]),abs(face_n[1]),abs(face_n[2])]
    horizontality = nz
    if(horizontality>0.9 and abs(z_min-computeZMin(face_p))<1):
           return "GroundSurface"
    if(horizontality<=0.1):
        return "WallSurface"
    else:
        return "RoofSurface"

def choosePoints(pList):
    l = len(pList)
    i1 = random.randint(0,l-1)
    i2 = random.randint(0,l-1)
    while (i1==i2):
        i2 = random.randint(0,l-1)
    i3 = random.randint(0,l-1)
    while (i1==i3 or i2==i3):
        i3 = random.randint(0,l-1)
    return (pList[i1], pList[i2], pList[i3])


def semantisation(objFile):
    id = (objFile.split("/")[-1]).split(".")[0]
    fileNormales.write('building '+id+'\n'+"==========================================="+'\n')
    vertices, normals, faces = read_obj_file(objFile)
    faces_n = []

    z_min = computeZMin(vertices)

    faces_type = []
    faces_p = []

    faceIndex = 0
    for f in faces:
        
        
        face_p = []
        for p in f:
            face_p+=[vertices[int(p.split('/')[0])-1]]
        faces_p+=[face_p]

        #n = [0,0,0]
        #for i in range (111):
        #    ni = computeNormal(f, vertices)
        #    n=[ni[0]+n[0]*i,ni[1]+n[1]*i,ni[2]+n[2]*i]
        #    n=[n[0]/(i+1.),n[1]/(i+1.),n[2]/(i+1.)]
        
        n = computeNormal(f, vertices)

        

        faces_n+=[n]

        

        face_type = semanticType(face_p, n, z_min)
        faces_type+=[face_type]
        fileNormales.write('\t '+str(faceIndex)+' : ['+str(n[0])+","+str(n[1])+","+str(n[2])+']'+' '+face_type+"\n")

        for p in face_p:
            fileNormales.write(' |||||| '+str(p[0])+', '+str(p[1])+', '+str(p[2])+'||')

        fileNormales.write('\n\n')
        faceIndex+=1

        

    

    
    fileNormales.write("==========================================="+'\n')

    createCityObject(id, faces_p, faces_type)
    return faces_type

def createCityObject(id, faces, types):
    
    co = CityObject(id=id)
    bdry =faces

    for i in range (len(bdry)):
        bdry[i] = [bdry[i]]

    bdry = bdry

    geom = Geometry(type='Solid', lod=2)
    geom.boundaries.append(bdry)

    srf = {
        0: {'surface_idx': [], 'type': 'WallSurface'},
        1: {'surface_idx': [], 'type': 'GroundSurface'},
        2: {'surface_idx': [], 'type': 'RoofSurface'}
    }

    for i in range (len(types)):
        j=-1
        if(types[i]=='WallSurface'):
            j=0
        elif(types[i]=='GroundSurface'):
            j=1
        elif(types[i]=='RoofSurface'):
            j=2
        srf[j]['surface_idx']+=[[0,i]]

    geom.surfaces = srf

    co.geometry.append(geom)
    co.type = 'Building'


    cm.cityobjects[co.id] = co

    cm2 = cityjson.CityJSON()

    cm2.cityobjects[co.id] = co

    cm2.add_to_j()
    cm2.update_bbox()

    outfile = RESULTS_DIR+ 'res_buildings/'+id+'.json'
    

    fo = open(outfile, "w")
    json_str = json.dumps(cm2.j, indent='\t')
    fo.write(json_str)
    fo.close()
    
    

    

def main():
    
    res = list(map(semantisation,objFiles))

    cm.add_to_j()
    cm.update_bbox()

    outfile = RESULTS_DIR+ 'result.json'
    

    fo = open(outfile, "w")
    json_str = json.dumps(cm.j, indent='\t')
    fo.write(json_str)
    fo.close()
    fileNormales.close()
    
    

if __name__ == "__main__":
    main()