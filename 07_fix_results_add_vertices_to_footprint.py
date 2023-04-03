#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os, sys
from utils import *
from shapely import Polygon, Point, LineString
from shapely.plotting import plot_polygon, plot_points
import argparse

# variables
city3d_results_dir = "data/IGN/results/"
output_dir = "data/IGN/results_fixed/"
delta_footprint=1e-6
delta_point_in_line=1e-8

def parse_args():
    parser = argparse.ArgumentParser("Fix footprint face by adding vertices at the bottom of wall faces")

    parser.add_argument("--city3d_results_dir", "-c",
                        help="Input directory containing city3d results", default="data/IGN/results")
    parser.add_argument("--output_dir", "-o",
                        help="Output directory for fixed results", default="data/IGN/results_footprint_fixed")
    parser.add_argument("--delta_footprint", "-d", 
                        help="Maximum distance for searching for new vertices", default="1e-6")
    parser.add_argument("--delta_point_in_line", "-p", 
                        help="Maximum distance for considering that a point belongs to a line", default="1e-8")
    return parser.parse_args()

def get_z_min(vertices):
    z_min = 9999
    for v in vertices:
        if v[2] < z_min:
            z_min = v[2]
    return z_min

def get_footprint_face(vertices,faces,z_min):
    footprint_vertices = []
    footprint_face_index = -1
    for idx, face in enumerate(faces):
        if (footprint_face_index != -1):
            break
        face_int = [int(i) for i in face]
        for index in face_int:
            if vertices[index-1][2] != z_min:
                break
            if index == face_int[-1]:
                footprint_vertices = [vertices[i-1] for i in face_int] + [vertices[face_int[0]-1]]
                footprint_face_index = idx
    return footprint_vertices, footprint_face_index

def get_vertices_to_add_to_footprint_face(vertices, footprint_vertices, z_min, delta_footprint):
    points_to_add = {}
    for idx, v in enumerate(vertices):
        if abs(v[2] - z_min) < delta_footprint and v not in footprint_vertices:
            points_to_add[Point(v)] = idx+1
    return points_to_add

def footprint_to_linestring_collection(footprint_vertices):
    footprint = Polygon(footprint_vertices)
    b = footprint.boundary.coords
    linestrings = [LineString(b[k:k+2]) for k in range(len(b) - 1)]
    return linestrings

def calculate_new_vertices_position(vertices_to_add, linestrings):
    # A dict of dict with the following structure
    # { polygon_line_index: {point_to_add: distance_from_line_start, point_to_add_2: distance_from_line_start, ... }, polygon_line_index_2: ...}
    vertices_position = {}
    points_matched = 0
    for point in vertices_to_add:
        for idx,line in enumerate(linestrings):
            if line.distance(point) < 1e-8:
                if idx not in vertices_position:
                    vertices_position[idx] = {}
                vertices_position[idx][point] = line.project(point, normalized=True)
                points_matched += 1
    return vertices_position, points_matched

def create_new_footprint_face(vertices_position, faces, footprint_face_index, footprint_vertices, vertices_to_add):
    # order by line index reversed
    vertices_position = dict(sorted(vertices_position.items(), reverse=True))
    points_added = 0
    new_footprint_face = faces[footprint_face_index]
    for line_idx,pt_pos in vertices_position.items():
        # order by distance from start of line reversed
        pt_pos = dict(sorted(pt_pos.items(), key=lambda item: item[1], reverse=True))
        for pt, pos in pt_pos.items():
            footprint_vertices.insert(line_idx+1, list(pt.coords[0]))
            new_footprint_face.insert(line_idx+1, str(vertices_to_add[pt]))
            points_added += 1
    return new_footprint_face, points_added

def cleanup_z(vertices):
    z = [v[2] for v in vertices]
    unique_z = sorted(set(z))
    replacements = {}
    for i in range(len(unique_z)-1):
        if abs(unique_z[i+1] - unique_z[i]) < 1e-12:
            if unique_z[i] not in replacements:
                replacements[unique_z[i+1]] = unique_z[i]
            else:
                replacements[unique_z[i+1]] = replacements[unique_z[i]]
    for z_to_replace,z_replacement in replacements.items():
        for index, vz in enumerate(z):
            if vz == z_to_replace:
                z[index] = z_replacement
    for i in range(len(z)):
        vertices[i][2] = z[i]
    return vertices

def main():

    recreate_dir(output_dir)

    for filename in os.listdir(city3d_results_dir):

        # if filename != "BATIMENT0000000320899175.obj":
        #     continue

        print("Attempting to fix " + filename)
        f = os.path.join(city3d_results_dir, filename)

        vertices, normals, faces = read_obj_file(f)

        vertices = cleanup_z(vertices)

        z_min = get_z_min(vertices)

        footprint_vertices, footprint_face_index = get_footprint_face(vertices, faces, z_min)
        if len(footprint_vertices) == 0:
            print("[fix_city3d_result] Could not find a footprint face in city3D result")
            sys.exit(1)

        vertices_to_add = get_vertices_to_add_to_footprint_face(vertices, footprint_vertices, z_min, delta_footprint)
        if len(vertices_to_add) == 0:
            # TODO: test if mesh already watertight here or before
            print("[fix_city3d_result] Could not find vertices to update footprint")
            write_obj_file(os.path.join(output_dir, filename), vertices, normals, faces)
            continue

        linestrings = footprint_to_linestring_collection(footprint_vertices)

        vertices_position, points_matched = calculate_new_vertices_position(vertices_to_add, linestrings)
        if (points_matched != len(vertices_to_add)):
            print("[fix_city3d_result] Not all points to add will be added")
            sys.exit(3)

        new_footprint_face, points_added = create_new_footprint_face(vertices_position, faces, footprint_face_index, footprint_vertices, vertices_to_add)
        if (points_added != len(vertices_to_add)):
            print("[fix_city3d_result] Not all points to add have been added")
            sys.exit(4)
        
        faces[footprint_face_index] = new_footprint_face

        print("Fixing successful for " + filename)

        write_obj_file(os.path.join(output_dir, filename), vertices, normals, faces)

if __name__ == "__main__":
    main()
