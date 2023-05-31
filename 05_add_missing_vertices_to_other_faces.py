#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os, sys
from utils import *
from shapely import Polygon, Point, LineString
from shapely.plotting import plot_polygon, plot_points
import argparse
import matplotlib.pyplot as plt
import time
from shapely.validation import explain_validity
import json 
from skspatial.objects import Line as skLine
from skspatial.objects import Point as skPoint
from tqdm import tqdm

def parse_args():
    parser = argparse.ArgumentParser("Try to fix results by adding necessary vertices to ground face edges")
    parser.add_argument("--city3d_results_dir", "-c",
                        help="Input directory containing city3d results", default="data/IGN/results_ground_face_fixed")
    parser.add_argument("--output_dir", "-o",
                        help="Output directory for fixed results", default="data/IGN/results_all_faces_fixed")
    parser.add_argument("--delta_point_in_line", "-p", 
                        help="Maximum distance for considering that a point belongs to a line", default="1e-6")
    parser.add_argument("--delta_coordinates", "-d", 
                    help="If the distance between two coordinates are under this threshold they are considered as the same", default="1e-8")#8
    return parser.parse_args()

# Returns face vertices as list of coordinates. Example below:
# [
#     [1.662060000002384, 4.509850000031292, 174.81], 
#     [4.610860000015236, -2.205880000256002, 174.81], 
#     [-0.6243600000161678, -4.458619999699295, 174.81], 
#     [-3.667009999975562, 2.230999999679625, 174.81]
# ]
def get_face_vertices(face, vertices):
    face_vertices = []
    # TODO: Handle faces index containing '/' or '//'
    vertices_index = [int(i) for i in face]
    # This list is not closing back on the first vertice
    face_vertices = [ vertices[i-1] for i in vertices_index ] 
    return face_vertices

# Returns face edges as list of start point and end point. Example below:
# [
#     [
#         [1.662060000002384, 4.509850000031292, 174.81],
#         [4.610860000015236, -2.205880000256002, 174.81]
#     ],
#     [
#         [4.610860000015236, -2.205880000256002, 174.81],
#         [-0.6243600000161678, -4.458619999699295, 174.81]
#     ],
#     [
#         [-0.6243600000161678, -4.458619999699295, 174.81],
#         [-3.667009999975562, 2.230999999679625, 174.81]
#     ],
#     [
#         [-3.667009999975562, 2.230999999679625, 174.81],
#         [1.662060000002384, 4.509850000031292, 174.81]
#     ]
# ]
def get_face_edges(face_vertices):
    # We close back the list on the first vertex to extract edges more easily
    face_vertices = face_vertices + [ face_vertices[0] ]
    # get a list of shapely edges
    edges = [face_vertices[k:k+2] for k in range(len(face_vertices) - 1)]
    return edges

# distance 3d point to 3d line
def get_distance(vertex, edge):

    is_between_edge_vertices = 1
    
    vertex = skPoint(vertex)
    line_start = skPoint(list(edge[0]))
    line_end = skPoint(list(edge[1]))

    # Get distance between 3d point and 3 line
    line = skLine.from_points(line_start, line_end)
    vertex_edge_distance = line.distance_point(vertex)

    # Project point along line and get position of projected point along line
    projected_point = line.project_point(vertex)
    distance_start_projected = line_start.distance_point(projected_point)
    distance_end_projected = line_end.distance_point(projected_point)
    edge_length = line_start.distance_point(line_end)

    # Test if point is between origin and start of the edge (naive approach)
    # TODO : implement a more elaborate solution
    if (distance_start_projected + distance_end_projected > edge_length + 1e-8):
        print("somme distance = " + str(distance_start_projected + distance_end_projected))
        print("taille edge = " + str(edge_length))
        is_between_edge_vertices = 0
        
    distance_projected_along_edge = float(distance_start_projected/edge_length)

    return vertex_edge_distance, projected_point, distance_projected_along_edge, is_between_edge_vertices

# return candidate vertices for a face as a json object. Example below:
# {
#  "0": { => edge index in local edge list (starting at 0)
#   "47": { => index of vertex as existing in obj file (starting at 1) that could be added to edge
#    "distance_along_edge": 0.04177091439217363, => distance between projected point and edge start along edge
#    "coordinates": [ => vertex coordinates
#     1.785234072362563,
#     4.22932781710834,
#     174.81
#    ],
#    "distance_to_edge": 4.440892098500626e-16, => distance between vertex and edge
#    "projected_vertex": [ => projected vertex coordinates
#     1.7852340723625626,
#     4.22932781710834,
#     174.81
#    ]
#   },
# ...
#  }
def get_candidate_vertices(face, vertices, min_distance):

    candidate_vertices = {}
    candidate_count = 0

    # get face vertices and edges
    face_vertices = get_face_vertices(face, vertices)
    edges = get_face_edges(face_vertices)

    # iterate over edges
    for e_idx,edge in enumerate(edges):

        added_coords = []

        xmin = min(edge[0][0],edge[1][0]) - min_distance
        ymin = min(edge[0][1],edge[1][1]) - min_distance
        zmin = min(edge[0][2],edge[1][2]) - min_distance
        xmax = max(edge[0][0],edge[1][0]) + min_distance
        ymax = max(edge[0][1],edge[1][1]) + min_distance
        zmax = max(edge[0][2],edge[1][2]) + min_distance
        # print(xmin)
        # print(ymin)
        # print(zmin)
        # print(xmax)
        # print(ymax)
        # print(zmax)

        for v_idx,vertex in enumerate(vertices):
            
            # ignore vertices already present in face
            if vertex in face_vertices:
                continue

            # Continue if vertex is not situated in 3D bbox surrounding edge
            if (vertex[0] < xmin or vertex[0] > xmax 
                or vertex[1] < ymin or vertex[1] > ymax 
                or vertex[2] < zmin or vertex[2] > zmax):
                continue

            # Get distance between line and vertex
            vertex_edge_distance, projected_point, distance_projected_along_edge, is_between_edge_vertices = get_distance(vertex,edge)
            # print(vertex)
            # print(projected_point)
            # print(vertex_edge_distance)
            # print(distance_projected_along_edge)
            # print(is_between_edge_vertices)

            # Continue if vertex projection on edge is not between edge start and end point
            if not is_between_edge_vertices:
                # print("is_between_edge_vertices removing " + str(v_idx+1))
                continue

            # Continue if vertex is at the start or at the end of edge
            # TODO: Is O or 1 ok or should we use something like a delta 1e-N ?
            if distance_projected_along_edge == 0.0 or distance_projected_along_edge == 1.0:
                continue

            # If vertex distance to edge is small enough and the new vertex has not already been added to the list of candidates
            if vertex_edge_distance < min_distance and vertex not in added_coords:
                if e_idx not in candidate_vertices:
                    candidate_vertices[e_idx] = {}
                vertex_info = {}
                vertex_info["distance_along_edge"] = distance_projected_along_edge
                vertex_info["coordinates"] = vertex
                vertex_info["distance_to_edge"] = vertex_edge_distance
                vertex_info["projected_vertex"] = projected_point.tolist()
                candidate_vertices[e_idx][v_idx+1] = vertex_info
                added_coords.append(vertex)
                candidate_count+=1
                
    return candidate_vertices, candidate_count

def cleanup_coordinates_on_axis(vertices, delta, axis):

    # get coordinates on given axis
    z = [v[axis] for v in vertices]
    # sort unique coordinates values
    unique_z = sorted(set(z))
    # dictionary that will contain values to replace
    replacements = {}
    # number of values replaced
    replacements_count = 0

    for i in range(len(unique_z)-1):
        # check difference between consecutive ordered coordinates 
        if abs(unique_z[i+1] - unique_z[i]) < delta:
            if unique_z[i] not in replacements:
                replacements[unique_z[i+1]] = unique_z[i]
            else:
                replacements[unique_z[i+1]] = replacements[unique_z[i]]

    # replace in axis coordinates
    for z_to_replace,z_replacement in replacements.items():
        for index, vz in enumerate(z):
            if vz == z_to_replace:
                z[index] = z_replacement
                replacements_count += 1

    # replace values in original coordinates
    for i in range(len(z)):
        vertices[i][axis] = z[i]

    return vertices, replacements_count


def replace_vertex(vertices, to_be_replaced, replacement):
    print("to be replaced " + str(to_be_replaced))
    new_vertices = vertices.copy()
    for v_idx,v in enumerate(vertices):
        if v == to_be_replaced:
            print("replacing " + str(new_vertices[v_idx]))
            print("with " + str(replacement))
            new_vertices[v_idx] = replacement
    return vertices

def add_candidates_to_face(face, vertices, candidate_vertices, use_projected_vertex):
    vertex_index = len(vertices)
    # We add vertex starting the last edge
    candidate_vertices = dict(sorted(candidate_vertices.items(), reverse=True))
    vertices_added = 0
    # Iterate over edges
    for edge_idx,vertex_to_add in candidate_vertices.items():
        # order vertex to add by distance along edge in reverse order
        vertex_entry = dict(sorted(vertex_to_add.items(), key=lambda item: item[1]["distance_along_edge"], reverse=True))
        for vertex_idx, vertex_info in vertex_entry.items():
            # insert vertex in vertices list
            if(use_projected_vertex):
                # add projected at the end of vertices list
                vertices.append(vertex_info["projected_vertex"])
                # replace existing coordinates with projected vertex value
                # print(vertices[vertex_idx-1])
                # vertices[vertex_idx-1] = vertex_info["projected_vertex"]
                # print(vertices[vertex_idx-1])
                vertices = replace_vertex(vertices, vertices[vertex_idx-1], vertex_info["projected_vertex"])
            else:
                # add vertex coorindates at the end of the vertices list
                vertices.append(vertex_info["coordinates"])
            vertex_index += 1
            # insert every vertex index after edge starting point
            # this way the first point added will be the last before edge last point at the end of the loop
            # face.insert(edge_idx+1, vertex_idx)
            face.insert(edge_idx+1, vertex_index)
            vertices_added += 1
    return face, vertices, vertices_added


def main():

    args = parse_args()
    # print(args)
    recreate_dir(args.output_dir)
    replaced_count = 0
    modified_count = 0
    total_count = 0

    for filename in tqdm(os.listdir(args.city3d_results_dir)):

        # print(filename)
        filepath = os.path.join(args.city3d_results_dir, filename)
        vertices, normals, faces = read_obj_file(filepath)
        
        total_replacement = 0
        # Merge very close coordinates values on all axis
        # TODO: Would it better to do it only for each point (x,y,z) ? 
        vertices, replacements_count = cleanup_coordinates_on_axis(vertices, float(args.delta_coordinates), 0)
        total_replacement += replacements_count
        # print(str(replacements_count) + " coordinates values have been aligned along x axis")
        vertices, replacements_count = cleanup_coordinates_on_axis(vertices, float(args.delta_coordinates), 1)
        total_replacement += replacements_count        
        # print(str(replacements_count) + " coordinates values have been aligned along y axis")
        vertices, replacements_count = cleanup_coordinates_on_axis(vertices, float(args.delta_coordinates), 2)
        total_replacement += replacements_count        
        # print(str(replacements_count) + " coordinates values have been aligned along z axis")

        if (total_replacement > 0):
            replaced_count += 1

        new_faces = faces.copy()
        
        vertices_added = 0

        for idx, face in enumerate(faces[:-1]):
            candidate_vertices, candidate_count = get_candidate_vertices(face, vertices, float(args.delta_point_in_line))
            new_face, vertices, number_vertices_added = add_candidates_to_face(face, vertices, candidate_vertices, False)
            vertices_added += number_vertices_added
            new_faces[idx] = new_face

        if (vertices_added > 0):
            modified_count += 1

        write_obj_file(os.path.join(args.output_dir, filename), vertices, normals, new_faces)

        total_count += 1
    
    print(str(modified_count) + "/" + str(total_count) + " obj files have been modified to fix the ground face")
    print(str(replaced_count) + "/" + str(total_count) + " obj files have been modified to align close coordinates")

if __name__ == "__main__":
    main()
