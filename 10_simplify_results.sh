#!/usr/bin/env bash

#############
# Variables #
#############

RESULTS_DIR="data/IGN/results_shifted/"
SIMPLIFICATION_OUTPUT_DIR="data/IGN/results_simplified/"
INPUT_CSV_FILE="params_simplify.csv"
JOBLOG_FILE="simplify.csv"
FAILED_FILE="failed_simplification.txt"
TIMEOUT_SECONDS=30

##############################
# Parameters file generation #
##############################

rm $INPUT_CSV_FILE 2> /dev/null

for f in "$RESULTS_DIR"*
do
    INPUT_RESULT_FILE=$(pwd)"/$f"
    FILENAME=$(basename "$INPUT_RESULT_FILE")
    OUTPUT_RESULT_FILE=$(pwd)"/$SIMPLIFICATION_OUTPUT_DIR$FILENAME"
    echo "$INPUT_RESULT_FILE,$OUTPUT_RESULT_FILE" >> $INPUT_CSV_FILE
done

#############################
# Recreate output directory #
#############################

if [ -d "$SIMPLIFICATION_OUTPUT_DIR" ]
then
    rm -rf $SIMPLIFICATION_OUTPUT_DIR
fi

mkdir $SIMPLIFICATION_OUTPUT_DIR

############################
# Launch cleanup processes #
############################

# remove existing log files
rm $JOBLOG_FILE 2> /dev/null
rm $FAILED_FILE 2> /dev/null

START=$(date +%s.%N)

# Launch cleanup in parallel jobs to speed things up
cat $INPUT_CSV_FILE | parallel --timeout $TIMEOUT_SECONDS --colsep ',' --jobs $(nproc) --joblog $JOBLOG_FILE ./Release/bin/CLI_Simplify_Mesh {1} {2} >> /dev/null 2>&1  

DURATION=$(echo "$(date +%s.%N) - $START" | bc)
EXECUTION_TIME=`printf "%.2f seconds" ${duration/./,}`
echo "Simplification Execution Time: $EXECUTION_TIME"

#########################
# List failed processes #
#########################

echo "======================"
echo "LIST OF FAILED SIMPLIFICATIONS"
echo "======================"

while IFS=$'\t' read -r Seq Host Starttime JobRuntime Send Receive Exitval Signal Command
do
    if [ "$Exitval" -eq "-1" ]
    then
        BUILDING_FAILURE=$(echo $Command | awk '{print $NF}' | xargs basename | cut -d '.' -f 1)
        echo $BUILDING_FAILURE >> $FAILED_FILE
        echo $BUILDING_FAILURE
        
    fi
done < <(tail -n +2 $JOBLOG_FILE)
