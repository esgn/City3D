#!/usr/bin/env bash

IGN_DIR="data/IGN/"
RESULTS_DIR=$IGN_DIR"results"
MOUNT_POINT="/mnt/IGNFAB/CITY3D_INPUT/"
SRC_LIDAR_PATCHES=$MOUNT_POINT"lidar_cropped_to_building_with_buffer_as_ply/"
DST_LIDAR_PATCHES=$IGN_DIR"lidar_crops_as_ply/"
SRC_FOOTPRINTS=$MOUNT_POINT"btopo_footprints_as_obj/"
DST_FOOTPRINTS=$IGN_DIR"bdtopo_footprints_as_obj/"

rm -rf $IGN_DIR
mkdir -p $IGN_DIR

rm -fr $RESULTS_DIR
mkdir -p $RESULTS_DIR

rm -rf $DST_LIDAR_PATCHES
mkdir -p $DST_LIDAR_PATCHES
cp $SRC_LIDAR_PATCHES* $DST_LIDAR_PATCHES

rm -rf $DST_FOOTPRINTS
mkdir -p $DST_FOOTPRINTS
cp $SRC_FOOTPRINTS* $DST_FOOTPRINTS
