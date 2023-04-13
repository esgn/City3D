#!/usr/bin/env bash

# To run this script a mount point /mnt/IGNFAB must be present locally
# This scripts creates all the necessary directories for the rest of the pipeline

MOUNT_POINT="/mnt/IGNFAB/CITY3D_INPUT/"
SOURCE_LIDAR_FILE="lidar.las"
SOURCE_FOOTPRINTS_FILE="footprints.gpkg"
SRC_LIDAR_FILE=$MOUNT_POINT$SOURCE_LIDAR_FILE
SRC_FOOTPRINTS_FILE=$MOUNT_POINT$SOURCE_FOOTPRINTS_FILE

IGN_DIR="data/IGN/"
SRC_FOOTPRINTS_DIR="source_footprints"
SRC_LIDAR_DIR="source_point_cloud"

rm -rf $IGN_DIR
mkdir -p $IGN_DIR
echo "$IGN_DIR recreated"

cd $IGN_DIR

mkdir -p $SRC_FOOTPRINTS_DIR
cd $SRC_FOOTPRINTS_DIR
cp $SRC_FOOTPRINTS_FILE .
cd ..
echo "$SRC_FOOTPRINTS_DIR recreated"


mkdir -p $SRC_LIDAR_DIR
cd $SRC_LIDAR_DIR
cp -r $SRC_LIDAR_FILE .
echo "$SRC_LIDAR_DIR recreated"
