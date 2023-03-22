#!/usr/bin/env bash

# To run this script a mount point /mnt/IGNFAB must be present locally
# This scripts creates all the necessary directories for the rest of the pipeline

MOUNT_POINT="/mnt/IGNFAB/CITY3D_INPUT/"
LIDAR_PATCHES_ARCHIVE="ply_extracts.tar.gz"
FOOTPRINTS_ARCHIVE="obj_footprints.tar.gz"
SRC_LIDAR_PATCHES=$MOUNT_POINT$LIDAR_PATCHES_ARCHIVE
SRC_FOOTPRINTS=$MOUNT_POINT$FOOTPRINTS_ARCHIVE

IGN_DIR="data/IGN/"
RESULTS_DIR=$IGN_DIR"results"
DST_LIDAR_PATCHES="ply_extracts"
DST_FOOTPRINTS="obj_footprints"

rm -rf $IGN_DIR
mkdir -p $IGN_DIR
echo "$IGN_DIR recreated"

rm -fr $RESULTS_DIR
mkdir -p $RESULTS_DIR
echo "$RESULTS_DIR recreated"

cd $IGN_DIR

# Copy LIDAR patches archive from mount point and untar
rm -rf $DST_LIDAR_PATCHES
cp $SRC_LIDAR_PATCHES .
tar -zxf $LIDAR_PATCHES_ARCHIVE
echo "$DST_LIDAR_PATCHES recreated"

# Copy footprints archive from mount point and untar
rm -rf $DST_FOOTPRINTSDST_FOOTPRINTS
cp $SRC_FOOTPRINTS .
tar -zxf $FOOTPRINTS_ARCHIVE 
echo "$DST_FOOTPRINTS recreated"
