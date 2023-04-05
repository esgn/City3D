#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os, sys
import fiona
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from shapely.geometry import shape, Polygon, box, MultiPolygon
from shapely.geometry.polygon import orient
import rasterio as rio
import requests
import shutil
from statistics import mean
from tqdm import tqdm
import argparse
import tarfile

# Retry for requests the easy way

requests_session = requests.Session()
retries = Retry(
    total=10,
    backoff_factor=1,
    status_forcelist=[429, 500, 501, 502, 503, 504],
    raise_on_status=True
)
requests_session.mount("http://", HTTPAdapter(max_retries=retries))
requests_session.mount("https://", HTTPAdapter(max_retries=retries))

# Global internal variables

temporary_tif = "temporary.tif"
single_obj_output_file = "merged_footprints.obj"

# Arguments parsing

def parse_args():
    parser = argparse.ArgumentParser("Export building footprints from a GPKG file to distinct OBJ files")
    parser.add_argument("--input_footprints", "-i",
                        help="Input footprints file as GPKG", default="data/IGN/source_footprints/footprints.gpkg")
    parser.add_argument("--output_dir", "-o",
                        help="Output directory for OBJ files", default="data/IGN/footprints_obj/")
    parser.add_argument("--dtm_res", "-d",
                        help="Digital Terrain Model resolution", default=1, type=int)
    parser.add_argument("--wms_queries", "-w",
                        help="Make WMS query for each footprint point", action='store_true')
    parser.add_argument("--z_for_each", "-z",
                        help="Give each footprint point its altitude", action='store_true')
    return parser.parse_args()

# Recreate output directory

def recreate_dir(output_dir):
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.mkdir(output_dir)

# Get IGN DTM extract based on a bounding box and a resolution

def get_dtm_extract(bbox, dtm_resolution):
    width = int((bbox[2] - bbox[0]) // dtm_resolution)
    height = int((bbox[3] - bbox[1]) // dtm_resolution)
    if width > 10000 or height > 10000:
        print("BBOX is too large. Closing down")
        sys.exit(0)
    query = f"https://wxs.ign.fr/altimetrie/geoportail/r/wms?REQUEST=GetMap&SERVICE=WMS&VERSION=1.3.0&CRS=EPSG:2154&BBOX={','.join([str(c) for c in bbox])}&LAYERS=ELEVATION.ELEVATIONGRIDCOVERAGE.HIGHRES&WIDTH={width}&HEIGHT={height}&FORMAT=image/geotiff&STYLES="
    r = requests_session.get(query)
    # rasterio in memory raster fails from time to time. Writing temporary file on disk
    with open(temporary_tif, "wb") as f:
        f.write(r.content)

# Update polygons altitude to set footprint at ground level using DTM

def update_polygon_z(polygon, dtm, z_for_each):
    new_coords = []
    # Get altitude for each polygon point
    for c in polygon.exterior.coords:
        # TODO: Handle errors if they happen
        query = rio.sample.sample_gen(dtm, [(c[0], c[1])])
        new_z = next(query)[0]
        new_coords.append((c[0], c[1], new_z))
    if not z_for_each:
        coords = list(zip(*new_coords))
        zs = list(coords[2])
        min_z = min(zs)
        temp_coords = []
        for c in new_coords:
            temp_coords.append((c[0], c[1], min_z))
        new_coords = temp_coords
    new_poly = Polygon(new_coords)
    return new_poly

# Write polygon as obj file. Naive approach. Normals are not calculated.

def write_to_obj(polygon, output_dir, filename, extension):
    global vertices
    global normals
    global faces
    vertex_index = len(vertices)
    vertex_count = 0
    path = os.path.join(output_dir, filename+extension)
    polygon = orient(polygon)
    with open(path, 'w') as obj_file:
        for c in polygon.exterior.coords[:-1]:
            vertex = ("v",)+c
            row = ' '.join(str(x) for x in vertex)+"\n"
            obj_file.write(row)
            vertices.append(row)
            vertex_count += 1
        for c in polygon.exterior.coords[:-1]:
            normal = "vn 0 0 -1\n"
            obj_file.write(normal)
            normals.append(normal)
        face = ["f"]+list(str(x)+"//"+str(x) for x in range(1, len(polygon.exterior.coords[:-1])+1))
        obj_file.write(' '.join(str(x) for x in face)+"\n")
        # This is only to write a single merged obj at the end
        face = ["f"]+list(str(x)+"//"+str(x) for x in range(vertex_index+1, vertex_index+vertex_count+1))
        faces.append(' '.join(str(x) for x in face)+"\n")

# Polygon handling

def process_building_polygon(polygon, cleabs, args):
    if args.wms_queries:
        bbox = polygon.buffer(args.dtm_res).bounds
        get_dtm_extract(bbox, args.dtm_res)
    dtm = rio.open(temporary_tif)
    geom = update_polygon_z(polygon, dtm, args.z_for_each)
    dtm.close()
    write_to_obj(geom, args.output_dir, cleabs, ".obj")

# In order to write a single OBJ file containing all polygons

def write_single_obj(output_dir, single_obj_output_file):
    global vertices
    global normals
    global faces
    with open(os.path.join(output_dir, single_obj_output_file), 'w') as output:
        for v in vertices:
            output.write(v)
        for n in normals:
            output.write(n)
        for f in faces:
            output.write(f)

# Make tar.gz file if needed

def make_tarfile(output_filename, source_dir):
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))

# Main

def main():

    args = parse_args()
    global vertices
    global normals
    global faces
    vertices, normals, faces = [], [], []

    recreate_dir(args.output_dir)

    with fiona.open(args.input_footprints) as source:

        #  Use a single wms query to get DTM extract on the extent of the input footprints file
        if not args.wms_queries:
            b = source.bounds
            bbox = box(b[0], b[1], b[2], b[3])
            bbox = bbox.buffer(args.dtm_res).bounds
            get_dtm_extract(bbox, args.dtm_res)

        # For all polygons in gpgk file
        for f in tqdm(source, position=0, leave=True):

            cleabs = f['properties']['cleabs']
            polygons = shape(f['geometry'])
            if(type(polygons)==Polygon):
                polygons = MultiPolygon([polygons])

            if len(polygons.geoms) > 1:
                # TODO: handle polygons with holes
                i = 0
                for polygon in polygons.geoms:
                    tqdm.write("[WARNING] Dealing with true multipolygon on " + cleabs)
                    process_building_polygon(polygon, cleabs+"_"+str(i), args)
                    i += 1
            else:
                process_building_polygon(polygons.geoms[0], cleabs, args)

        # cleanup
        os.remove(temporary_tif)
        # write all polygons in a single file
        write_single_obj(args.output_dir, single_obj_output_file)

if __name__ == "__main__":
    main()
