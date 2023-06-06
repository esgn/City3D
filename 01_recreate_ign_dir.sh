#!/usr/bin/env bash

# To run this script a mount point /mnt/IGNFAB must be present locally
# This scripts creates all the necessary directories for the rest of the pipeline

MOUNT_POINT="/mnt/IGNFAB"
DATASET="Marseille_zone_test_periurbaine_1"
#DATASET="Marseille_zone_test_periurbaine_2"
#DATASET="Marseille_zone_test_urbaine_1"
#DATASET="Marseille_zone_test_urbaine_2"
FOOTPRINTS_FILENAME="BUEmprise2D_Peri1_2_clean.gpkg"
#FOOTPRINTS_FILENAME="BUEmprise2D_Peri2_2_clean.gpkg"
#FOOTPRINTS_FILENAME="BUEmprise2D_Urbain1_2_clean.gpkg"
#FOOTPRINTS_FILENAME="BUEmprise2D_Urbain2_2_clean.gp
SOURCE_PATH="${MOUNT_POINT}/CHANTIER_MARSEILLE/ZONES_TEST/${DATASET}"
SOURCE_LIDAR_FILE_PATH="${SOURCE_PATH}/LIDAR_V4/LIDAR_CROPPED_CLASSIFICATION_AGREGEE/${DATASET}.laz"
SOURCE_FOOTPRINTS_FILE_PATH="${SOURCE_PATH}/EMPRISES_2D/EMPRISES_MAQUETTE_NETTOYEES_V2/${FOOTPRINTS_FILENAME}"

LOCAL_IGN_DIR="data/IGN/"
LOCAL_FOOTPRINTS_DIR="source_footprints"
LOCAL_FOOTPRINTS_FILENAME="footprints.gpkg"
LOCAL_LIDAR_DIR="source_point_cloud"
LOCAL_LIDAR_FILENAME="lidar.las"

rm -rf ${LOCAL_IGN_DIR}
mkdir -p ${LOCAL_IGN_DIR}
echo "${LOCAL_IGN_DIR} recreated"

cd ${LOCAL_IGN_DIR}

mkdir -p ${LOCAL_FOOTPRINTS_DIR}
cd ${LOCAL_FOOTPRINTS_DIR}
cp ${SOURCE_FOOTPRINTS_FILE_PATH} ${LOCAL_FOOTPRINTS_FILENAME}
cd ..
echo "${LOCAL_FOOTPRINTS_DIR} recreated"

mkdir -p ${LOCAL_LIDAR_DIR}
cd ${LOCAL_LIDAR_DIR}
cp ${SOURCE_LIDAR_FILE_PATH} ${LOCAL_LIDAR_FILENAME}
echo "${LOCAL_LIDAR_DIR} recreated"
