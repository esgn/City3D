cmake_minimum_required(VERSION 3.1)

# Set directory name as project name
get_filename_component(PROJECT_NAME ${CMAKE_CURRENT_SOURCE_DIR} NAME)
project(${PROJECT_NAME})

# specify C++ standard
set(CMAKE_CXX_STANDARD 11)

# Set Easy3D directory
set(Easy3D_DIR ${CMAKE_CURRENT_LIST_DIR}/../Easy3D-2.5.2/Release)

# request Easy3D (recommended to request only needed components)
find_package(Easy3D REQUIRED)

# create an executable target
set(${PROJECT_NAME}_basic_SOURCES
    basic.cpp
)
add_executable(${PROJECT_NAME}_basic ${${PROJECT_NAME}_basic_SOURCES})

# create an executable target
set(${PROJECT_NAME}_triangle_SOURCES
    triangle.cpp
)
add_executable(${PROJECT_NAME}_triangle ${${PROJECT_NAME}_triangle_SOURCES})

# link to necessary Easy3D modules (add more if needed, e.g., algo)
target_link_libraries(${PROJECT_NAME}_basic easy3d::algo_ext easy3d::algo easy3d::core easy3d::util easy3d::fileio)
target_link_libraries(${PROJECT_NAME}_triangle easy3d::algo_ext easy3d::algo easy3d::core easy3d::util easy3d::fileio)

# The resources directory
target_compile_definitions(
    ${PROJECT_NAME}_basic
    PRIVATE
    "EASY3D_ROOT_DIR=\"${CMAKE_CURRENT_LIST_DIR}\""
)

# The resources directory
target_compile_definitions(
    ${PROJECT_NAME}_triangle
    PRIVATE
    "EASY3D_ROOT_DIR=\"${CMAKE_CURRENT_LIST_DIR}\""
)
