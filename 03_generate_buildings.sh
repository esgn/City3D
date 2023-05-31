#!/usr/bin/env bash

# This scripts generates building using City3D and parrallel to speed things up 
# and automatically kill hanging process after a certain timeout

#############
# Variables #
#############

EXECUTABLE_PATH="./Release/bin/CLI_IGN_LIDAR_Footprints"
DATA_DIR="data/IGN/"
LIDAR_DIR=$DATA_DIR"point_cloud_extracts_ply_shifted/"
OBJ_DIR=$DATA_DIR"footprints_obj_below_pcd_shifted/"
RESULTS_DIR_NAME="results/"
ORIGIN_DIR_NAME="origin_shift/"
RESULTS_DIR=$DATA_DIR$RESULTS_DIR_NAME
ORIGIN_DIR=$DATA_DIR$ORIGIN_DIR_NAME
INPUT_CSV_FILE="params_generate.csv"
JOBLOG_FILE="city3d.csv"
TIMEOUT_FILE="reconstruction_timeout.txt"
ERROR_FILE="reconstruction_error.txt"
SERVER_DIR="/var/www/html/data/"
TIMEOUT_SECONDS=1200
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

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
rm $TIMEOUT_FILE 2> /dev/null
rm $ERROR_FILE 2> /dev/null

START=$(date +%s.%N)

# Launch city3D in parallel jobs to speed things up
cat $INPUT_CSV_FILE | parallel --timeout $TIMEOUT_SECONDS --colsep ',' --jobs $(nproc) --joblog $JOBLOG_FILE $EXECUTABLE_PATH {1} {2} {3} >> /dev/null 2>&1  

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
        echo $BUILDING_FAILURE >> $ERROR_FILE
        
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
        echo $BUILDING_FAILURE >> $TIMEOUT_FILE
        
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

##############################
# Create archive and copy it #
##############################

TAR_NAME="results_$(date +%s).tar.gz"
tar czf $TAR_NAME -C $DATA_DIR $RESULTS_DIR_NAME $ORIGIN_DIR_NAME -C $SCRIPT_DIR $JOBLOG_FILE $ERROR_FILE $TIMEOUT_FILE
cp $TAR_NAME $SERVER_DIR
rm $TAR_NAME
