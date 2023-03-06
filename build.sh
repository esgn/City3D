#!/usr/bin/env bash

BUILD_DIR="Release"
CGAL_VERSION="5.2.2"

# Download CGAL (to be used as header only)
wget "https://github.com/CGAL/cgal/releases/download/v$CGAL_VERSION/CGAL-$CGAL_VERSION.tar.xz" .
tar -xf CGAL-$CGAL_VERSION.tar.xz
rm CGAL-$CGAL_VERSION.tar.xz

# Recreate build dir
if [ -d "$BUILD_DIR" ]
then
    rm -rf $BUILD_DIR
fi

# Compile alpha shape executable
mkdir $BUILD_DIR
cd $BUILD_DIR
cmake -DCMAKE_BUILD_TYPE=Release ..
make -j$(($(nproc)))

