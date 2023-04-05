#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os, sys
import fiona
import argparse
import shutil
from shapely.geometry import shape, box, Polygon, MultiPolygon
import pdal
import time
import glob

def parse_args():
    parser = argparse.ArgumentParser("Export LIDAR as .ply extracts with normals for each given footprint")
    parser.add_argument("--input_footprints", "-i",
                        help="Input footprints file as GPKG", default="data/IGN/source_footprints/footprints.gpkg")
    parser.add_argument("--footprint_buffer", "-b", default=5,
                        help="Buffer to add to each footprint when cropping")
    parser.add_argument("--input_pointcloud", "-p",
                        help="Input Pointcloud (las or laz)", default="data/IGN/source_point_cloud/zone_urbaine/")
    parser.add_argument("--output_dir", "-o",
                        help="Output directory for ply extracts", default="data/IGN/point_cloud_extracts_ply")
    return parser.parse_args()

def recreate_dir(dir_name):
    if os.path.exists(dir_name):
        shutil.rmtree(dir_name)
    os.mkdir(dir_name)

def bufferize_and_get_bounds(polygon, buffer_size):
   b = polygon.buffer(buffer_size).bounds
   return box(b[0],b[1],b[2],b[3])

def get_footprints_bbox(input_footprints, footprint_buffer):
    footprints_bbox_as_polygons={}
    with fiona.open(input_footprints) as src:
        for f in src:
            cleabs = f['properties']['cleabs']
            polygons = shape(f['geometry'])
            if(type(polygons)==Polygon):
                polygons = MultiPolygon([polygons])
            if len(polygons.geoms) > 1:
                i = 0
                for polygon in polygons.geoms:
                    bbox = bufferize_and_get_bounds(polygon, footprint_buffer)
                    footprints_bbox_as_polygons[cleabs+"_"+str(i)] = bbox
                    i+=1
            else:
                bbox = bufferize_and_get_bounds(polygons, footprint_buffer)
                footprints_bbox_as_polygons[cleabs] = bbox
    return footprints_bbox_as_polygons

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
    print("Pipeline LOG : ", pipeline.log)

def rename_extracts(output_dir,sorted_bbox):
    index=1
    for building_id in sorted_bbox:
        os.rename(os.path.join(output_dir,str(index)+".ply"), os.path.join(output_dir,str(building_id)+".ply"))
        index+=1

if __name__ == "__main__":
    t0 = time.time()
    args = parse_args()
    features_bbox_as_polygons = get_footprints_bbox(args.input_footprints, args.footprint_buffer)
    recreate_dir(args.output_dir)
    sorted_bbox = dict(sorted(features_bbox_as_polygons.items()))

    lidar_files = glob.glob(args.input_pointcloud+"*.las")
    list(map(lambda file:crop_las(file, sorted_bbox, args.output_dir), lidar_files))

    rename_extracts(args.output_dir, sorted_bbox)
    print(f"processing time: {time.time() - t0}")
