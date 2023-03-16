#!/usr/bin/env bash

# This scripts generates building using City3D and parrallel to speed things up 
# and automatically kill hanging process after a certain timeout

input_csv_file="params.csv"
joblog_file="city3d.csv"
failed_file="failed.txt"
start=$(date +%s.%N)
# a large timeout is required for certain buildings
# a large timeout is necessary to kill endless process which occurs for some builing
timeout_seconds=1200

# remove existing log files
rm $joblog_file 2> /dev/null
rm $failed_file 2> /dev/null

# Launch city3D in parallel jobs to speed things up
cat $input_csv_file | parallel --timeout $timeout_seconds --colsep ',' --jobs $(nproc) --joblog $joblog_file ./Release/bin/CLI_IGN_LIDAR_Footprints {1} {2} {3} >> /dev/null 2>&1  

duration=$(echo "$(date +%s.%N) - $start" | bc)
execution_time=`printf "%.2f seconds" ${duration/./,}`
echo "City3D Execution Time: $execution_time"

echo ""
echo "LIST OF FAILED RECONSTRUCTIONS"
echo "=============================="
while IFS=$'\t' read -r Seq Host Starttime JobRuntime Send Receive Exitval Signal Command
do
    if [ "$Exitval" -eq "-1" ]
    then
        building_failure=$(echo $Command | awk '{print $NF}' | xargs basename | cut -d '.' -f 1)
        echo $building_failure >> $failed_file
        echo $building_failure
        
    fi
done < <(tail -n +2 $joblog_file)
