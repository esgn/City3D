#!/usr/bin/env bash

lidar_dir="data/IGN/ply_extracts/"
obj_dir="data/IGN/obj_footprints/"
result_dir="data/IGN/results/"
input_failed_file="failed.txt"
output_params_file="params_failed.csv"

rm -rf $output_params_file

while IFS= read -r line; do
    building_id=$line
    input_pcd_file=$(pwd)"/"$lidar_dir$building_id".ply"
    input_footprint_file="$(pwd)"/"$obj_dir$building_id".obj
    result_file="$(pwd)"/"$result_dir$building_id".obj
    echo "$input_pcd_file","$input_footprint_file","$result_file" >> $output_params_file
done < $input_failed_file

joblog_file="city3d_retry_failed.csv"
start=$(date +%s.%N)
timeout_seconds=600

# remove existing files
rm $joblog_file 2> /dev/null
rm $failed_file 2> /dev/null

# Launch city3D in parallel jobs to speed things up
cat $output_params_file | parallel --timeout $timeout_seconds --colsep ',' --jobs $(nproc) --joblog $joblog_file ./Release/bin/CLI_IGN_LIDAR_Footprints {1} {2} {3} >> /dev/null 2>&1  
