cmake_minimum_required(VERSION 3.1)

get_filename_component(PROJECT_NAME ${CMAKE_CURRENT_SOURCE_DIR} NAME)
project(${PROJECT_NAME})

set(${PROJECT_NAME}_SOURCES
        main.cpp
        )

find_package(Eigen3 3.3.7)
if (EIGEN3_FOUND)
  include( ${EIGEN3_USE_FILE} )
endif()

add_executable(${PROJECT_NAME} ${${PROJECT_NAME}_SOURCES})

set_target_properties(${PROJECT_NAME} PROPERTIES FOLDER "CLI examples")

target_link_libraries(${PROJECT_NAME} basic math model method)

# The resources directory
target_compile_definitions(
        ${PROJECT_NAME}
        PRIVATE
        "CITY3D_ROOT_DIR=\"${CITY3D_ROOT}\""
)