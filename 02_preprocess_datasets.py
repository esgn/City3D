#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os, sys
import fiona
import pdal
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from shapely.geometry import shape, Polygon, box, MultiPolygon
from shapely.geometry.polygon import orient
import rasterio as rio
import requests
from statistics import mean
from tqdm import tqdm
import argparse
from utils import *
from shapely import force_2d
import open3d as o3d
import numpy as np
import time

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
merged_obj_output_file = "merged_footprints.obj"

# Arguments parsing

def parse_args():
    parser = argparse.ArgumentParser("Preprocess source datasets for City3D")

    parser.add_argument("--input_footprints", "-f",
                        help="Input footprints file as GPKG", default="data/IGN/source_footprints/footprints.gpkg")
    parser.add_argument("--input_pcd", "-p",
                        help="Input Pointcloud (las or laz)", default="data/IGN/source_point_cloud/lidar.las")
    
    parser.add_argument("--output_footprints_dir", "-g",
                        help="Output directory for OBJ files", default="data/IGN/footprints_obj")
    parser.add_argument("--output_pcd_dir", "-q",
                        help="Output directory for ply extracts", default="data/IGN/point_cloud_extracts_ply")
    parser.add_argument("--output_origins_dir", "-x",
                        help="Output directory for origin files", default="data/IGN/origin_shift")
    
    parser.add_argument("--dtm_res", "-d",
                        help="Digital Terrain Model resolution", default=1, type=int)
    parser.add_argument("--z_for_each", "-z",
                        help="Give each footprint point its respective altitude. If false all points are set with minimum altitude", action='store_true')
    parser.add_argument("--footprint_buffer", "-b", default=5,
                        help="Buffer to add to each footprint when cropping")
    parser.add_argument("--z_gap", "-a",
                            help="Gap that will be applied to put footprint under point cloud z min", default="0.5")
    
    return parser.parse_args()

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

# Get BBOX of polygon + buffer

def bufferize_and_get_bounds(polygon, buffer_size):
   b = polygon.buffer(buffer_size).bounds
   return box(b[0],b[1],b[2],b[3])

# Process each polygon to update its vertices altitude

def process_and_write_polygon(polygon, cleabs, output_dir, z_for_each):
    dtm = rio.open(temporary_tif)
    geom = update_polygon_z(polygon, dtm, z_for_each)
    dtm.close()
    write_to_obj(geom, output_dir, cleabs+".obj")

# Upddate vertices altitude inside a polygon

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

# write polygon to obj file

def write_to_obj(polygon, output_dir, filename):
    polygon = orient(polygon)
    vertices, normals, faces = [],[],[]
    for c in polygon.exterior.coords[:-1]:
        vertices.append (list(c))
        normals.append([0,0,-1])
    faces=[[*range(1, len(polygon.exterior.coords[:-1])+1)]]
    write_obj_file(os.path.join(output_dir, filename), vertices, normals, faces, 2)

# Crop las based on bbox list using pdal

def crop_las(input_pointcloud, features_bbox_as_polygons, output_dir):
    pipeline = pdal.Reader(input_pointcloud)
    all_bounds = [f"([{minx}, {maxx}], [{miny}, {maxy}])"
                  for minx, miny, maxx, maxy in [x.bounds for x in features_bbox_as_polygons.values()]]
    pipeline |= pdal.Filter.crop(bounds=all_bounds)
    pipeline |= pdal.Filter.range(limits="Classification[2:17]")
    pipeline |= pdal.Filter.normal(knn=8)
    pipeline |= pdal.Filter.ferry(dimensions="NormalX => nx, NormalY => ny, NormalZ => nz")
    pipeline |= pdal.Writer.ply(filename=os.path.join(output_dir, "#.ply"), dims="X,Y,Z,nx,ny,nz", precision=6)
    pipeline.execute()

def ensure_footprint_below_pcd(input_pcd_dir, input_footprints_dir, output_footprints_dir, z_gap):
     for f in tqdm(os.listdir(input_pcd_dir)):

        # building identifier
        cleabs = f.split(".")[0]
        
        # Load min_z from obj 
        vertices, normals, faces = read_obj_file( os.path.join(input_footprints_dir, cleabs+".obj") )
        z_obj =  min([v[2] for v in vertices])
        polygon = force_2d(Polygon(vertices))

        # Pdal pipeline to crop lidar with footprint
        pipeline = pdal.Reader( os.path.join(input_pcd_dir,f) )
        pipeline |= pdal.Filter.crop(polygon=polygon.wkt)
        pipeline |= pdal.Filter.locate(dimension="Z", minmax="min")
        pipeline.execute()

        # Get z_min from pcd
        try:
            z_pcd_min = pipeline.arrays[0][0][2]
        except:
            print("CROPPING ISSUE WITH FOOTPRINT ON " + cleabs)
            write_obj_file(os.path.join(output_footprints_dir,cleabs+".obj"),vertices, normals, faces)
            continue

        #  Fix z_obj if necessary
        if z_pcd_min <= z_obj:
            for index, vz in enumerate(vertices):
                vertices[index][2] = (z_pcd_min-float(z_gap))
        
        write_obj_file(os.path.join(output_footprints_dir,cleabs+".obj"),vertices, normals, faces)

# def shift datasets

def shift_datasets(input_pcd_dir, input_footprints_dir, output_pcd_dir, output_footprints_dir, output_origin_dir):
    for f in tqdm(os.listdir(input_pcd_dir)):
        # building identifier
        cleabs = f.split(".")[0]
        # read poincloud patch ply file
        pcd = o3d.io.read_point_cloud(os.path.join(input_pcd_dir, f))
        # get point cloud center
        center = pcd.get_center()
        # We keep only x and y center as we dont want to shift altitudes
        center[2] = 0
        # We want to shift with round values to avoid rounding issues
        center = [float(round(c)) for c in center]
        # make sure center is numpy.ndarray[numpy.float64[3, 1]]
        center = np.array(center,  dtype='float64')
        # shift point cloud
        pcd.translate(center*-1, relative=True)
        # write resulting point cloud with global shift
        o3d.io.write_point_cloud(os.path.join(output_pcd_dir, f), pcd, write_ascii=True)
        # load obj footprint file
        vertices, normals, faces = read_obj_file(os.path.join(input_footprints_dir, cleabs+".obj"))
        # write obj footprint file with global shift
        write_obj_file(os.path.join(output_footprints_dir, cleabs+".obj"), vertices-center, normals, faces)
        # write center coordinates in a .origin file
        with open(os.path.join(output_origin_dir, cleabs+".origin"),'w') as origin:
                center = center
                origin.write(' '.join(str(x) for x in center))

# Main

def main():

    args = parse_args()

    recreate_dir(args.output_footprints_dir)
    recreate_dir(args.output_pcd_dir)
    recreate_dir(args.output_origins_dir)
    recreate_dir(args.output_footprints_dir+"_shifted")
    recreate_dir(args.output_pcd_dir+"_shifted")
    recreate_dir(args.output_footprints_dir+"_below_pcd")
    recreate_dir(args.output_footprints_dir+"_below_pcd_shifted")

    with fiona.open(args.input_footprints) as source:

        start = time.time()

        # Use a single wms query to get DTM extract on the extent of the input footprints file
        print(" => Downloading DTM extract")
        b = source.bounds
        bbox = box(b[0], b[1], b[2], b[3])
        bbox = bbox.buffer(args.dtm_res).bounds
        get_dtm_extract(bbox, args.dtm_res)
        end_1 = time.time()
        print(str(int(end_1-start)) + " seconds elapsed")

        # To store footprints bbox as polygons
        footprints_bbox_as_polygons={}
        
        print(" => Export footprints to obj")
        # For all polygons in footprints file
        for f in tqdm(source, position=0, leave=True):

            # Will work for majority of datasets
            cleabs=f['id']

            polygons = shape(f['geometry'])

            # Handle everything as multipolygon if case of mixed geometry types
            if(type(polygons)==Polygon):
                polygons = MultiPolygon([polygons])
            
            # Write all footprint polygons as obj and accumulate bbox for LIDAR cropping
            if len(polygons.geoms) > 1:
                i = 0
                for polygon in polygons.geoms:
                    tqdm.write("[INFO] Dealing with true multipolygon on " + cleabs)
                    process_and_write_polygon(polygon, cleabs+"_"+str(i), args.output_footprints_dir, args.z_for_each)
                    bbox = bufferize_and_get_bounds(polygon, args.footprint_buffer)
                    footprints_bbox_as_polygons[cleabs+"_"+str(i)] = bbox
                    i += 1
            else:
                process_and_write_polygon(polygons.geoms[0], cleabs, args.output_footprints_dir, args.z_for_each)
                bbox = bufferize_and_get_bounds(polygons, args.footprint_buffer)
                footprints_bbox_as_polygons[cleabs] = bbox
        end_2 = time.time()
        print(str(int(end_2-end_1)) + " seconds elapsed")

        # remove dtm extract
        os.remove(temporary_tif)

        # write all footprint polygons in a single file
        print(" => Merge all obj into single file")
        write_merged_obj_files(args.output_footprints_dir, merged_obj_output_file)
        end_3 = time.time()
        print(str(int(end_3-end_2)) + " seconds elapsed")

        # crop las 
        print(" => Crop LAS file to footprints + buffer")
        crop_las(args.input_pcd, footprints_bbox_as_polygons, args.output_pcd_dir)
        end_4 = time.time()
        print(str(int(end_4-end_3)) + " seconds elapsed")

        # make sure footprints are below pcd
        print(" => Ensure footprints are below pcd")
        ensure_footprint_below_pcd(args.output_pcd_dir, args.output_footprints_dir, args.output_footprints_dir+"_below_pcd", args.z_gap)
        end_5 = time.time()
        print(str(int(end_5-end_4)) + " seconds elapsed")

        # shift to local coordinates footprints and pcd extracts
        print(" => Shift datasets coordinates")
        shift_datasets(args.output_pcd_dir, args.output_footprints_dir+"_below_pcd", args.output_pcd_dir+"_shifted", args.output_footprints_dir+"_below_pcd_shifted", args.output_origins_dir)
        end_6 = time.time()
        print(str(int(end_6-end_5)) + " seconds elapsed")

        print(" => TOTAL TIME : " + str(int(end_6-start)) + " seconds")

if __name__ == "__main__":
    main()
