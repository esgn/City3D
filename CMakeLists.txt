cmake_minimum_required(VERSION 3.1)

set(CITY3D_GIT_ROOT  ${CMAKE_CURRENT_LIST_DIR})

# If we want to compile against local CGAL as header only
# set(CGAL_DIR ${CITY3D_GIT_ROOT}/CGAL-5.5.2)
# set(CGAL_DATA_DIR ${CITY3D_GIT_ROOT}/CGAL-5.5.2)

project(City3D)

add_subdirectory(code)
