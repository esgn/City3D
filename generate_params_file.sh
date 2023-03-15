#!/usr/bin/env bash

lidar_dir="data/IGN/ply_extracts/"
obj_dir="data/IGN/obj_footprints/"
result_dir="data/IGN/results/"
output_csv_file="params.csv"

rm -rf $output_csv_file

for f in "$lidar_dir"*
do
    input_point_cloud_file="$(pwd)"/$f
    filename=$(basename "$input_point_cloud_file" .ply)
    input_footprint_file="$(pwd)"/"$obj_dir$filename".obj
    result_file="$(pwd)"/"$result_dir$filename".obj
    echo "$input_point_cloud_file","$input_footprint_file","$result_file" >> $output_csv_file
done
