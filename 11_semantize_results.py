from utils import *
import glob
import random
import math
import json
import argparse
import os, sys
from skspatial.objects import Plane
from cjio import cityjson
from cjio.models import CityObject, Geometry
from shapely.geometry import Polygon

def parse_args():
    parser = argparse.ArgumentParser("OBJ to cityjson with semantics")
    parser.add_argument("--input_dir", "-i",
                        help="Input directory containing fixed results in LAMB93 coordinates", default="data/IGN/results_shifted")
    parser.add_argument("--output_dir", "-o",
                        help="Input directory containing origin files", default="data/IGN/cityjson_results")
    return parser.parse_args()

def semanticType(face_p, face_n, z_min):
    [nx,ny,nz]=[abs(face_n[0]),abs(face_n[1]),abs(face_n[2])]
    horizontality = nz
    if(horizontality>0.9 and abs(z_min-computeAverageZMin(face_p))<0.1):
           return "GroundSurface"
    if(horizontality<=0.1):
        return "WallSurface"
    else:
        return "RoofSurface"
    
def createCityObject(id, faces, types, results_dir, cm):
    
    co = CityObject(id=id)
    geom = Geometry(type='Solid', lod=2)
    geom.boundaries.append([[f] for f in faces])
    srf = {
        0: {'surface_idx': [], 'type': 'WallSurface'},
        1: {'surface_idx': [], 'type': 'GroundSurface'},
        2: {'surface_idx': [], 'type': 'RoofSurface'}
    }

    for i in range(len(types)):
        if(types[i]=='WallSurface'):
            j=0
        elif(types[i]=='GroundSurface'):
            j=1
        elif(types[i]=='RoofSurface'):
            j=2
        else:
            print("could not determine surface type. Exiting")
            sys.exit(5)
        srf[j]['surface_idx']+=[[0,i]]

    geom.surfaces = srf
    co.geometry.append(geom)
    co.type = 'Building'
    cm.cityobjects[co.id] = co

    cm2 = cityjson.CityJSON()
    cm2.cityobjects[co.id] = co
    cm2.add_to_j()
    cm2.update_bbox()
    outfile = os.path.join(results_dir, 'res_buildings', id+'.json')

    fo = open(outfile, "w")
    json_str = json.dumps(cm2.j, indent='\t')
    fo.write(json_str)
    fo.close()        

def main():

    args = parse_args()
    objs = glob.glob(os.path.join(args.input_dir,'*.obj'))
    recreate_dir(args.output_dir)
    recreate_dir(os.path.join(args.output_dir,'res_buildings'))
    cm = cityjson.CityJSON()

    for obj in objs:
        filename = os.path.basename(obj)
        id = filename.split('.')[0]
        # if id != "231":
        #     continue
        vertices, normals, faces = read_obj_file(obj)
        # Get minimum z of the current building mesh
        z_min = computeZMin(vertices)
        output_faces = []
        types = []
        for face in faces:
            face_vertices = get_face_vertices(face,vertices,face_format=1)
            try:
                normal = normalize(Plane.best_fit(face_vertices).normal)
                type = semanticType(face_vertices, normal, z_min)
            except Exception as e:
                print("Could not semantize a face in " + obj)
                continue
            output_faces.append(face_vertices)
            types.append(type)
        createCityObject(id, output_faces, types, args.output_dir, cm)
    
    cm.add_to_j()
    cm.update_bbox()
    outfile = os.path.join(args.output_dir, 'result.json')

    fo = open(outfile, "w")
    json_str = json.dumps(cm.j, indent='\t')
    fo.write(json_str)
    fo.close()

if __name__ == "__main__":
    main()
