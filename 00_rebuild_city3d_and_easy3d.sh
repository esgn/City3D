#!/usr/bin/env bash

# This script build City3D and Easy3D executables

BUILD_DIR="Release"
CGAL_VERSION="5.2.2"
EASY3D_VERSION="2.5.2"
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Download CGAL and Easy3D
# CGAL will be used as header only
# Easy3D needs to be built

cd $SCRIPT_DIR
if [ ! -d "CGAL-$CGAL_VERSION" ]
then
    wget "https://github.com/CGAL/cgal/releases/download/v$CGAL_VERSION/CGAL-$CGAL_VERSION.tar.xz" .
    tar -xf CGAL-$CGAL_VERSION.tar.xz
    rm CGAL-$CGAL_VERSION.tar.xz
fi

if [ ! -d "Easy3D-$EASY3D_VERSION" ]
then
    wget "https://github.com/LiangliangNan/Easy3D/archive/refs/tags/v$EASY3D_VERSION.tar.gz" .
    tar -xf v$EASY3D_VERSION.tar.gz
    rm v$EASY3D_VERSION.tar.gz
fi

# Build Easy3D

cd Easy3D-$EASY3D_VERSION
if [ -d "$BUILD_DIR" ]
then
    rm -rf $BUILD_DIR
fi
mkdir $BUILD_DIR
cd $BUILD_DIR
cmake -DCMAKE_BUILD_TYPE=Release -DEasy3D_ENABLE_CGAL=ON -DCGAL_DIR=$SCRIPT_DIR/CGAL-$CGAL_VERSION ..
make -j$(($(nproc)))

# Build City3D

cd $SCRIPT_DIR
if [ -d "$BUILD_DIR" ]
then
    rm -rf $BUILD_DIR
fi
mkdir $BUILD_DIR
cd $BUILD_DIR
cmake -DCMAKE_BUILD_TYPE=Release ..
make -j$(($(nproc)))

# Build Easy3D fix executable
cd $SCRIPT_DIR/CLI_Easy3D_Fix
if [ -d "$BUILD_DIR" ]
then
    rm -rf $BUILD_DIR
fi
mkdir $BUILD_DIR
cd $BUILD_DIR
cmake -DCMAKE_BUILD_TYPE=Release ..
make -j$(($(nproc)))
 