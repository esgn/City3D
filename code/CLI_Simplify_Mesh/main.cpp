#include <CGAL/Simple_cartesian.h>
#include <CGAL/Surface_mesh.h>
#include <CGAL/Surface_mesh_simplification/edge_collapse.h>
#include <CGAL/Surface_mesh_simplification/Policies/Edge_collapse/Count_ratio_stop_predicate.h>
#include <CGAL/Polygon_mesh_processing/bbox.h>
#include <CGAL/Polygon_mesh_processing/IO/polygon_mesh_io.h>

#include <iostream>
#include <string>


namespace PMP = CGAL::Polygon_mesh_processing;
namespace SMS = CGAL::Surface_mesh_simplification;

typedef CGAL::Simple_cartesian<double>               Kernel;
typedef Kernel::Point_3                              Point_3;
typedef CGAL::Surface_mesh<Point_3>                  Surface_mesh;

using Mesh = CGAL::Surface_mesh<Point_3>;

int main(int argc, char** argv){

    std::cout.precision(17);
    // Read the input
    const std::string filename = (argc > 1) ? argv[1] : CGAL::data_file_path("data/IGN/test.obj");
    std::cout << "Reading " << filename << "..." << std::endl;
    const char *outfilename = (argc > 2) ? argv[2] : "data/IGN/test_simplified.obj";

    Mesh mesh;
    if(!PMP::IO::read_polygon_mesh(filename, mesh) || is_empty(mesh) || !is_triangle_mesh(mesh))
    {
        std::cerr << "Invalid input." << std::endl;
        return EXIT_FAILURE;
    }
    if(!CGAL::is_triangle_mesh(mesh))
    {
        std::cerr << "Input geometry is not triangulated." << std::endl;
        return EXIT_FAILURE;
    }

    std::cout << "Input: " << num_vertices(mesh) << " vertices, " << num_faces(mesh) << " faces" << std::endl;

    // In this example, the simplification stops when the number of undirected edges
    // drops below 10% of the initial count
    double stop_ratio = 0.02;
    SMS::Count_ratio_stop_predicate<Surface_mesh> stop(stop_ratio);
    
    int r = SMS::edge_collapse(mesh, stop);
    std::cout << "\nFinished!\n" << r << " edges removed.\n" << mesh.number_of_edges() << " final edges.\n";

    // Save the result
    
    std::cout << "Writing to " << outfilename << std::endl;
    CGAL::IO::write_polygon_mesh(outfilename, mesh, CGAL::parameters::stream_precision(17));


    return EXIT_SUCCESS;
}