#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>
#include <CGAL/Surface_mesh.h>
#include <CGAL/alpha_wrap_3.h>
#include <CGAL/Polygon_mesh_processing/bbox.h>
#include <CGAL/Polygon_mesh_processing/IO/polygon_mesh_io.h>
#include <CGAL/Real_timer.h>
#include <iostream>
#include <string>

namespace AW3 = CGAL::Alpha_wraps_3;
namespace PMP = CGAL::Polygon_mesh_processing;

using K = CGAL::Exact_predicates_inexact_constructions_kernel;
using Point_3 = K::Point_3;

using Mesh = CGAL::Surface_mesh<Point_3>;

int main(int argc, char** argv){

    std::cout.precision(17);
    // Read the input
    const std::string filename = (argc > 1) ? argv[1] : CGAL::data_file_path("data/IGN/test.obj");
    std::cout << "Reading " << filename << "..." << std::endl;
    const char *outfilename = (argc > 2) ? argv[2] : "data/IGN/result/test_simplified.obj";

    Mesh mesh;
    if(!PMP::IO::read_polygon_mesh(filename, mesh) || is_empty(mesh) || !is_triangle_mesh(mesh))
    {
        std::cerr << "Invalid input." << std::endl;
        return EXIT_FAILURE;
    }

    std::cout << "Input: " << num_vertices(mesh) << " vertices, " << num_faces(mesh) << " faces" << std::endl;



    return EXIT_SUCCESS;
}