#!/usr/bin/env bash

# This script build City3D executables

BUILD_DIR="Release"

# If we want to download CGAL and use it as header only
CGAL_VERSION="5.5.2"
if [ ! -d "CGAL-$CGAL_VERSION" ]
then
    # Download CGAL (to be used as header only)
    echo "toto"
    wget "https://github.com/CGAL/cgal/releases/download/v$CGAL_VERSION/CGAL-$CGAL_VERSION.tar.xz" .
    tar -xf CGAL-$CGAL_VERSION.tar.xz
    rm CGAL-$CGAL_VERSION.tar.xz
fi

# Recreate build dir
if [ -d "$BUILD_DIR" ]
then
    rm -rf $BUILD_DIR
fi

# Compile City3D release executables
mkdir $BUILD_DIR
cd $BUILD_DIR
cmake -DCMAKE_BUILD_TYPE=Release ..
make -j$(($(nproc)))
