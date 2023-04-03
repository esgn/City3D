#!/usr/bin/env bash

# This scripts generates building using City3D and parrallel to speed things up 
# and automatically kill hanging process after a certain timeout

#############
# Variables #
#############

LIDAR_DIR="data/IGN/point_cloud_extracts_ply_shifted/"
OBJ_DIR="data/IGN/footprints_obj_shifted_fixed/"
RESULTS_DIR="data/IGN/results/"
INPUT_CSV_FILE="params_generate.csv"
JOBLOG_FILE="city3d.csv"
TIMEOUT_SECONDS=1200

##############################
# Parameters file generation #
##############################

rm $INPUT_CSV_FILE 2> /dev/null

for f in "$LIDAR_DIR"*
do
    INPUT_PCD_FILE="$(pwd)"/$f
    FILENAME=$(basename "$INPUT_PCD_FILE" .ply)
    INPUT_FOOTPRINT_FILE="$(pwd)"/"$OBJ_DIR$FILENAME".obj
    RESULT_FILE="$(pwd)"/"$RESULTS_DIR$FILENAME".obj
    echo "$INPUT_PCD_FILE","$INPUT_FOOTPRINT_FILE","$RESULT_FILE" >> $INPUT_CSV_FILE
done

#############################
# Recreate output directory #
#############################

if [ -d "$RESULTS_DIR" ]
then
    rm -rf $RESULTS_DIR
fi

mkdir $RESULTS_DIR

###########################
# Launch city3d processes #
###########################

# remove existing log files
rm $JOBLOG_FILE 2> /dev/null
rm $FAILED_FILE 2> /dev/null

START=$(date +%s.%N)

# Launch city3D in parallel jobs to speed things up
cat $INPUT_CSV_FILE | parallel --timeout $TIMEOUT_SECONDS --colsep ',' --jobs $(nproc) --joblog $JOBLOG_FILE ./Release/bin/CLI_IGN_LIDAR_Footprints {1} {2} {3} >> /dev/null 2>&1  

DURATION=$(echo "$(date +%s.%N) - $START" | bc)
EXECUTION_TIME=`printf "%.2f seconds" ${DURATION/./,}`
echo "City3D Execution Time: $EXECUTION_TIME"

#########################
# List failed processes #
#########################

echo "==============================="
echo " POINT CLOUD COULD NOT BE READ "
echo "==============================="

while IFS=$'\t' read -r Seq Host Starttime JobRuntime Send Receive Exitval Signal Command
do
    if [ "$Exitval" -eq "10" ]
    then
        BUILDING_FAILURE=$(echo $Command | awk '{print $NF}' | xargs basename | cut -d '.' -f 1)
        echo $BUILDING_FAILURE
        
    fi
done < <(tail -n +2 $JOBLOG_FILE)

echo "============================="
echo " FOOTPRINT COULD NOT BE READ "
echo "============================="

while IFS=$'\t' read -r Seq Host Starttime JobRuntime Send Receive Exitval Signal Command
do
    if [ "$Exitval" -eq "11" ]
    then
        BUILDING_FAILURE=$(echo $Command | awk '{print $NF}' | xargs basename | cut -d '.' -f 1)
        echo $BUILDING_FAILURE
        
    fi
done < <(tail -n +2 $JOBLOG_FILE)


echo "======================="
echo " RECONSTRUCTION ERRROR "
echo "======================="

while IFS=$'\t' read -r Seq Host Starttime JobRuntime Send Receive Exitval Signal Command
do
    if [ "$Exitval" -eq "13" ]
    then
        BUILDING_FAILURE=$(echo $Command | awk '{print $NF}' | xargs basename | cut -d '.' -f 1)
        echo $BUILDING_FAILURE
        echo $BUILDING_FAILURE >> "reconstrution_error.txt"
        
    fi
done < <(tail -n +2 $JOBLOG_FILE)

echo "========================"
echo " RECONSTRUCTION TIMEOUT "
echo "========================"

while IFS=$'\t' read -r Seq Host Starttime JobRuntime Send Receive Exitval Signal Command
do
    if [ "$Exitval" -eq "-1" ]
    then
        BUILDING_FAILURE=$(echo $Command | awk '{print $NF}' | xargs basename | cut -d '.' -f 1)
        echo $BUILDING_FAILURE
        echo $BUILDING_FAILURE >> "reconstrution_timeout.txt"
        
    fi
done < <(tail -n +2 $JOBLOG_FILE)

echo "========================"
echo " COULD NOT WRITE RESULT "
echo "========================"

while IFS=$'\t' read -r Seq Host Starttime JobRuntime Send Receive Exitval Signal Command
do
    if [ "$Exitval" -eq "12" ]
    then
        BUILDING_FAILURE=$(echo $Command | awk '{print $NF}' | xargs basename | cut -d '.' -f 1)
        echo $BUILDING_FAILURE
        
    fi
done < <(tail -n +2 $JOBLOG_FILE)
