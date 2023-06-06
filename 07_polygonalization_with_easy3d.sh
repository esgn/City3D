#!/usr/bin/env bash

#############
# Variables #
#############

EXECUTABLE_PATH="./CLI_Easy3D_Fix/Release/CLI_Easy3D_Fix_basic"
CITY3D_RESULTS_DIR="data/IGN/results_fixed_with_cgal/"
FIX_OUTPUT_DIR="data/IGN/results_fixed_with_easy3d/"
INPUT_CSV_FILE="params_easy3d_fix.csv"
JOBLOG_FILE="easy3d_fix.csv"
FAILED_FILE="failed_easy3d_fix.txt"
TIMEOUT_SECONDS=120

##############################
# Parameters file generation #
##############################

rm $INPUT_CSV_FILE 2> /dev/null

for f in "$CITY3D_RESULTS_DIR"*
do
    INPUT_RESULT_FILE=$(pwd)"/$f"
    FILENAME=$(basename "$INPUT_RESULT_FILE")
    OUTPUT_RESULT_FILE=$(pwd)"/$FIX_OUTPUT_DIR$FILENAME"
    echo "$INPUT_RESULT_FILE,$OUTPUT_RESULT_FILE" >> $INPUT_CSV_FILE
done

#############################
# Recreate output directory #
#############################

if [ -d "$FIX_OUTPUT_DIR" ]
then
    rm -rf $FIX_OUTPUT_DIR
fi

mkdir $FIX_OUTPUT_DIR

############################
# Launch cleanup processes #
############################

# remove existing log files
rm $JOBLOG_FILE 2> /dev/null
rm $FAILED_FILE 2> /dev/null

START=$(date +%s.%N)

# Launch cleanup in parallel jobs to speed things up
cat $INPUT_CSV_FILE | parallel --timeout $TIMEOUT_SECONDS --colsep ',' --jobs $(nproc) --joblog $JOBLOG_FILE $EXECUTABLE_PATH {1} {2} >> /dev/null 2>&1  

DURATION=$(echo "$(date +%s.%N) - $START" | bc)
EXECUTION_TIME=`printf "%.2f seconds" ${DURATION/./,}`
echo "Cleanup Execution Time: $EXECUTION_TIME"

#########################
# List failed processes #
#########################

echo "============================="
echo "LIST OF FAILED POLYGONIZATION"
echo "============================="

while IFS=$'\t' read -r Seq Host Starttime JobRuntime Send Receive Exitval Signal Command
do
    if [ "$Exitval" -ne "0" ] || [ "$Signal" -ne "0" ]
    then
        BUILDING_FAILURE=$(echo $Command | awk '{print $NF}' | xargs basename | cut -d '.' -f 1)
        echo $BUILDING_FAILURE >> $FAILED_FILE
        echo $BUILDING_FAILURE
    fi
done < <(tail -n +2 $JOBLOG_FILE)
